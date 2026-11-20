import http from 'node:http';
import { randomUUID } from 'node:crypto';
import { pathToFileURL } from 'node:url';
import { TextDecoder } from 'node:util';

export const limits = Object.freeze({ bodyBytes: 4096, titleCodePoints: 80, records: 1000 });
const idPattern = /^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$/;
const keyPattern = /^[A-Za-z0-9._:-]{1,128}$/;
const requestIdPattern = /^[A-Za-z0-9._:-]{1,128}$/;
const utcPattern = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}\.\d{3}Z$/;

class ApiError extends Error {
  constructor(status, code, message) {
    super(message);
    this.status = status;
    this.code = code;
  }
}

function hasUnpairedSurrogate(value) {
  for (let index = 0; index < value.length; index += 1) {
    const current = value.charCodeAt(index);
    if (current >= 0xD800 && current <= 0xDBFF) {
      const next = value.charCodeAt(index + 1);
      if (!(next >= 0xDC00 && next <= 0xDFFF)) return true;
      index += 1;
    } else if (current >= 0xDC00 && current <= 0xDFFF) return true;
  }
  return false;
}

function validateBody(body) {
  if (!body || Array.isArray(body) || typeof body !== 'object'
      || Object.keys(body).length !== 1 || !Object.hasOwn(body, 'title')) {
    throw new ApiError(422, 'invalid_request', 'Body must contain only a title string.');
  }
  if (typeof body.title !== 'string' || !body.title.trim()
      || hasUnpairedSurrogate(body.title) || [...body.title].length > limits.titleCodePoints) {
    throw new ApiError(422, 'invalid_request', 'Title must contain 1 to 80 Unicode scalar values and non-whitespace content.');
  }
  // Preserve accepted text exactly: no hidden trim, normalization or truncation.
  return { title: body.title };
}

function readJson(request, maxBytes, timeoutMs) {
  const length = request.headers['content-length'];
  if (typeof length === 'string' && /^\d+$/.test(length) && Number(length) > maxBytes) {
    request.resume();
    return Promise.reject(new ApiError(413, 'payload_too_large', 'JSON body exceeds the byte limit.'));
  }
  return new Promise((resolve, reject) => {
    const chunks = [];
    let bytes = 0;
    let settled = false;
    const timer = setTimeout(() => finish(new ApiError(408, 'request_timeout', 'Request body did not complete in time.')), timeoutMs);
    timer.unref();
    const cleanup = () => {
      clearTimeout(timer);
      request.off('data', onData);
      request.off('end', onEnd);
      request.off('error', onError);
      request.off('aborted', onAborted);
    };
    const finish = (error, value) => {
      if (settled) return;
      settled = true;
      cleanup();
      if (error) {
        request.resume();
        reject(error);
      } else resolve(value);
    };
    const onData = (chunk) => {
      bytes += chunk.length;
      if (bytes > maxBytes) {
        finish(new ApiError(413, 'payload_too_large', 'JSON body exceeds the byte limit.'));
        return;
      }
      chunks.push(chunk);
    };
    const onEnd = () => {
      try {
        const text = new TextDecoder('utf-8', { fatal: true }).decode(Buffer.concat(chunks, bytes));
        finish(null, JSON.parse(text));
      } catch {
        finish(new ApiError(400, 'invalid_json', 'Body must be valid UTF-8 JSON.'));
      }
    };
    const onError = () => finish(new ApiError(400, 'invalid_json', 'Request body could not be read.'));
    const onAborted = () => finish(new ApiError(400, 'invalid_json', 'Request body was interrupted.'));
    request.on('data', onData);
    request.on('end', onEnd);
    request.on('error', onError);
    request.on('aborted', onAborted);
  });
}

function integerOption(value, min, max, label) {
  if (!Number.isInteger(value) || value < min || value > max) throw new TypeError(`Invalid ${label}.`);
  return value;
}

/**
 * A local in-memory example, not durable idempotency or production auth.
 * authenticate(request, { signal }) returns a server-verified { accountId } or null.
 * No header, bearer string or account parameter is trusted by the default.
 */
export function createContractServer({
  authenticate,
  now = () => new Date(),
  newId = () => `item_${randomUUID()}`,
  newRequestId = () => randomUUID(),
  maxBodyBytes = limits.bodyBytes,
  maxRecords = limits.records,
  bodyTimeoutMs = 5000,
  authTimeoutMs = 5000,
} = {}) {
  if (authenticate !== undefined && typeof authenticate !== 'function') throw new TypeError('authenticate must be a function.');
  for (const [label, value] of Object.entries({ now, newId, newRequestId })) {
    if (typeof value !== 'function') throw new TypeError(`${label} must be a function.`);
  }
  integerOption(maxBodyBytes, 1, 65536, 'maxBodyBytes');
  integerOption(maxRecords, 1, 10000, 'maxRecords');
  integerOption(bodyTimeoutMs, 1, 60000, 'bodyTimeoutMs');
  integerOption(authTimeoutMs, 1, 60000, 'authTimeoutMs');
  const items = new Map();
  const receipts = new Map();

  const server = http.createServer({ maxHeaderSize: 8192, requestTimeout: 10000, headersTimeout: 10000 }, (request, response) => {
    let requestId = randomUUID();
    const send = (status, body, extraHeaders = {}) => {
      if (response.destroyed || response.writableEnded) return;
      const payload = Buffer.from(JSON.stringify(body));
      response.writeHead(status, {
        'content-type': 'application/json; charset=utf-8',
        'content-length': payload.length,
        'cache-control': 'no-store',
        'x-request-id': requestId,
        ...extraHeaders,
      });
      response.end(payload);
    };
    const fail = (error) => {
      const known = error instanceof ApiError;
      const status = known ? error.status : 500;
      // Close unread request bodies without retaining unbounded bytes.
      request.resume();
      response.shouldKeepAlive = false;
      send(status, { error: { code: known ? error.code : 'internal_error', message: known ? error.message : 'The request could not be completed.' }, requestId }, { connection: 'close' });
    };

    const handle = async () => {
      const generated = newRequestId();
      if (typeof generated !== 'string' || !requestIdPattern.test(generated)) throw new Error('Invalid request ID adapter result.');
      requestId = generated;
      const url = new URL(request.url, 'http://localhost');
      if (url.pathname === '/health' && request.method === 'GET') {
        send(200, { status: 'ok' });
        return;
      }
      const createRoute = url.pathname === '/v1/items';
      const itemMatch = /^\/v1\/items\/([A-Za-z0-9][A-Za-z0-9_-]{0,127})$/.exec(url.pathname);
      if (!createRoute && !itemMatch) throw new ApiError(404, 'not_found', 'Resource not found.');
      const expectedMethod = createRoute ? 'POST' : 'GET';
      if (request.method !== expectedMethod) {
        response.setHeader('allow', expectedMethod);
        throw new ApiError(405, 'method_not_allowed', 'Method is not supported for this resource.');
      }
      let principal;
      if (authenticate) {
        const controller = new AbortController();
        let timer;
        try {
          const deadline = new Promise((_, reject) => {
            timer = setTimeout(() => {
              controller.abort();
              reject(new Error('Authentication deadline exceeded.'));
            }, authTimeoutMs);
            timer.unref();
          });
          principal = await Promise.race([authenticate(request, { signal: controller.signal }), deadline]);
        } catch {
          throw new ApiError(503, 'auth_unavailable', 'Authentication is temporarily unavailable.');
        } finally { clearTimeout(timer); }
      }
      if (!principal || typeof principal.accountId !== 'string' || !keyPattern.test(principal.accountId)) {
        throw new ApiError(401, 'unauthorized', 'A verified application session is required.');
      }
      const accountId = principal.accountId;
      if (url.search) throw new ApiError(400, 'invalid_request', 'Query parameters are not supported.');
      if (itemMatch) {
        const stored = items.get(itemMatch[1]);
        if (!stored || stored.accountId !== accountId) throw new ApiError(404, 'not_found', 'Resource not found.');
        send(200, stored.item);
        return;
      }
      const contentType = request.headers['content-type'];
      if (typeof contentType !== 'string' || !/^application\/json(?:\s*;\s*charset=utf-8)?\s*$/i.test(contentType)) {
        throw new ApiError(415, 'unsupported_media_type', 'Use application/json with UTF-8 encoding.');
      }
      const key = request.headers['idempotency-key'];
      if (typeof key !== 'string' || !keyPattern.test(key)) throw new ApiError(400, 'invalid_idempotency_key', 'Provide an Idempotency-Key of 1 to 128 allowed ASCII characters.');
      const body = validateBody(await readJson(request, maxBodyBytes, bodyTimeoutMs));
      const fingerprint = JSON.stringify(body);
      const scope = JSON.stringify([accountId, key]);

      // Intentionally synchronous check-and-commit: atomic within THIS process
      // while it stays alive. A real service needs a durable DB transaction.
      const receipt = receipts.get(scope);
      if (receipt) {
        if (receipt.fingerprint !== fingerprint) throw new ApiError(409, 'idempotency_conflict', 'The key was already used with a different payload.');
        send(201, receipt.item, { 'idempotency-replayed': 'true' });
        return;
      }
      if (items.size >= maxRecords) throw new ApiError(503, 'capacity_reached', 'The local demonstration store is full.');
      const id = newId();
      const date = now();
      if (typeof id !== 'string' || !idPattern.test(id) || items.has(id) || !(date instanceof Date) || !Number.isFinite(date.valueOf())) {
        throw new Error('Invalid data adapter result.');
      }
      const createdAt = date.toISOString();
      if (!utcPattern.test(createdAt)) throw new Error('Unsupported demonstration timestamp.');
      const item = Object.freeze({ id, title: body.title, createdAt, revision: '1' });
      items.set(id, { accountId, item });
      receipts.set(scope, { fingerprint, item });
      send(201, item, { 'idempotency-replayed': 'false' });
    };
    handle().catch(fail);
  });
  server.keepAliveTimeout = 1000;
  return server;
}

// Manual startup is opt-in. Importing this module never binds a socket.
if (process.argv[1] && import.meta.url === pathToFileURL(process.argv[1]).href) {
  const args = process.argv.slice(2);
  if (args.length && (args.length !== 2 || args[0] !== '--port' || !/^\d+$/.test(args[1]))) {
    console.error('Usage: node server.mjs [--port 0..65535]');
    process.exitCode = 2;
  } else {
    const port = args.length ? Number(args[1]) : 8787;
    if (!Number.isInteger(port) || port < 0 || port > 65535) {
      console.error('Port must be between 0 and 65535.');
      process.exitCode = 2;
    } else {
      const server = createContractServer();
      server.on('error', () => { console.error('Could not start the local demonstration server.'); process.exitCode = 1; });
      server.listen(port, '127.0.0.1', () => {
        console.log(`Local contract demonstration: http://127.0.0.1:${server.address().port}`);
        console.log('Writes are denied: no production authentication adapter is configured.');
      });
    }
  }
}
