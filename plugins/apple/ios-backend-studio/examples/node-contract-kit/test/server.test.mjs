import { test } from 'node:test';
import assert from 'node:assert/strict';
import { once } from 'node:events';
import { readFile } from 'node:fs/promises';
import { Readable } from 'node:stream';
import { createContractServer, limits } from '../server.mjs';

const itemFixture = JSON.parse(await readFile(new URL('../fixtures/item.json', import.meta.url), 'utf8'));
const errorFixture = JSON.parse(await readFile(new URL('../fixtures/invalid-request.json', import.meta.url), 'utf8'));
const openapi = JSON.parse(await readFile(new URL('../openapi.json', import.meta.url), 'utf8'));

// Synthetic authority for test accounts ONLY, not production header validation.
const fixtureAuth = (request) => {
  const accountId = request.headers['x-fixture-account'];
  return ['account-a', 'account-b'].includes(accountId) ? { accountId } : null;
};

async function start(t, options = {}) {
  const server = createContractServer({ authenticate: fixtureAuth, ...options });
  assert.equal(server.listening, false, 'import/factory must not bind a socket');
  server.listen(0, '127.0.0.1');
  await once(server, 'listening');
  t.after(() => new Promise((resolve) => {
    server.close(resolve);
    server.closeAllConnections();
  }));
  return `http://127.0.0.1:${server.address().port}`;
}

async function send(origin, { title = 'Café 🚀', key = 'operation-1', account = 'account-a', path = '/v1/items', method = 'POST', body, headers = {}, ...rest } = {}) {
  const response = await fetch(origin + path, {
    method,
    headers: { 'content-type': 'application/json', 'idempotency-key': key, 'x-fixture-account': account, ...headers },
    ...(method === 'GET' || method === 'HEAD' ? {} : { body: body ?? JSON.stringify({ title }) }),
    ...rest,
  });
  return { response, body: await response.json() };
}

function assertError(result, status, code) {
  assert.equal(result.response.status, status);
  assert.equal(result.body.error.code, code);
  assert.equal(result.body.requestId, result.response.headers.get('x-request-id'));
  assert.deepEqual(Object.keys(result.body).sort(), ['error', 'requestId']);
  assert.ok(openapi.components.schemas.Failure.properties.error.properties.code.enum.includes(code));
}

test('default server denies writes even with fabricated account and bearer headers', async (t) => {
  const origin = await start(t, { authenticate: undefined });
  const health = await fetch(origin + '/health');
  assert.deepEqual(await health.json(), { status: 'ok' });
  const result = await send(origin, { headers: { authorization: 'Bearer test-only-not-a-session', 'x-account-id': 'account-a' } });
  assertError(result, 401, 'unauthorized');
});

test('actual HTTP creation matches the shared Unicode/string-ID/UTC fixture', async (t) => {
  const origin = await start(t, { newId: () => itemFixture.id, now: () => new Date(itemFixture.createdAt) });
  const result = await send(origin);
  assert.equal(result.response.status, 201);
  assert.deepEqual(result.body, itemFixture);
  assert.equal(result.response.headers.get('idempotency-replayed'), 'false');
  assert.deepEqual(Object.keys(result.body).sort(), openapi.components.schemas.Item.required.toSorted());
  assert.equal(typeof result.body.id, 'string');
  assert.equal(typeof result.body.revision, 'string');
  assert.match(result.body.createdAt, new RegExp(openapi.components.schemas.Item.properties.createdAt.pattern));
});

test('GET resolves a stored resource only in its authenticated account', async (t) => {
  const origin = await start(t);
  const created = await send(origin);
  const own = await send(origin, { method: 'GET', path: '/v1/items/' + created.body.id });
  assert.equal(own.response.status, 200);
  assert.deepEqual(own.body, created.body);
  const other = await send(origin, { method: 'GET', account: 'account-b', path: '/v1/items/' + created.body.id });
  assertError(other, 404, 'not_found');
});

test('concurrent same-account same-key requests create one item and replay one receipt', async (t) => {
  let generated = 0;
  const origin = await start(t, { newId: () => `item_${++generated}` });
  const results = await Promise.all(Array.from({ length: 12 }, () => send(origin, { key: 'concurrent-operation' })));
  assert.equal(generated, 1);
  assert.ok(results.every((result) => result.response.status === 201));
  assert.equal(new Set(results.map((result) => JSON.stringify(result.body))).size, 1);
  assert.equal(results.filter((result) => result.response.headers.get('idempotency-replayed') === 'false').length, 1);
  assert.equal(results.filter((result) => result.response.headers.get('idempotency-replayed') === 'true').length, 11);
});

test('same account/key with another valid payload produces a conflict', async (t) => {
  const origin = await start(t);
  await send(origin, { key: 'conflict-operation', title: 'Original' });
  const conflict = await send(origin, { key: 'conflict-operation', title: 'Changed' });
  assertError(conflict, 409, 'idempotency_conflict');
});

test('same idempotency key is independent across verified accounts', async (t) => {
  let generated = 0;
  const origin = await start(t, { newId: () => `item_${++generated}` });
  const [a, b] = await Promise.all([send(origin, { key: 'shared-key', account: 'account-a' }), send(origin, { key: 'shared-key', account: 'account-b' })]);
  assert.equal(a.response.status, 201);
  assert.equal(b.response.status, 201);
  assert.notEqual(a.body.id, b.body.id);
  assert.equal(generated, 2);
});

test('unknown body fields, including authority claims, are rejected', async (t) => {
  const origin = await start(t);
  for (const body of ['{"title":"Valid","accountId":"account-b"}', '{"title":"Valid","__proto__":{"role":"admin"}}']) {
    assertError(await send(origin, { body }), 422, 'invalid_request');
  }
});

test('malformed JSON and invalid UTF-8 receive stable JSON errors', async (t) => {
  const origin = await start(t);
  assertError(await send(origin, { body: '{"title":' }), 400, 'invalid_json');
  assertError(await send(origin, { body: Buffer.from([0x7B, 0xFF, 0x7D]) }), 400, 'invalid_json');
});

test('known oversized body is rejected with a bounded JSON error', async (t) => {
  const origin = await start(t);
  const result = await send(origin, { body: JSON.stringify({ title: 'x'.repeat(limits.bodyBytes + 1) }) });
  assertError(result, 413, 'payload_too_large');
});

test('title limit counts Unicode scalar values rather than UTF-16 units', async (t) => {
  const origin = await start(t);
  const exact = await send(origin, { key: 'unicode-limit-ok', title: '🚀'.repeat(80) });
  assert.equal(exact.response.status, 201);
  assert.equal([...exact.body.title].length, 80);
  assert.equal(exact.body.title.length, 160);
  assertError(await send(origin, { key: 'unicode-limit-bad', title: '🚀'.repeat(81) }), 422, 'invalid_request');
});

test('invalid root/title shapes and unpaired surrogate escapes are rejected', async (t) => {
  const origin = await start(t);
  for (const body of ['null', '[]', '"a title"', '{}', '{"title":7}', '{"title":"   "}', '{"title":"\\ud800"}', '{"title":"\\udc00"}']) {
    assertError(await send(origin, { body }), 422, 'invalid_request');
  }
});

test('media type is explicit and non-UTF-8 declarations are refused', async (t) => {
  const origin = await start(t);
  for (const type of ['text/plain', 'application/json; charset=latin1']) {
    assertError(await send(origin, { headers: { 'content-type': type } }), 415, 'unsupported_media_type');
  }
});

test('error fixture and response request ID agree without reflecting client authority', async (t) => {
  const origin = await start(t, { newRequestId: () => errorFixture.requestId });
  const result = await send(origin, { body: '{}' });
  assert.equal(result.response.status, 422);
  assert.deepEqual(result.body, errorFixture);
  assert.equal(result.response.headers.get('x-request-id'), errorFixture.requestId);
});

test('routing, methods and unsupported query input use the declared error envelope', async (t) => {
  const origin = await start(t);
  assertError(await send(origin, { path: '/unknown' }), 404, 'not_found');
  const method = await send(origin, { method: 'GET' });
  assertError(method, 405, 'method_not_allowed');
  assert.equal(method.response.headers.get('allow'), 'POST');
  assertError(await send(origin, { path: '/v1/items?accountId=account-b' }), 400, 'invalid_request');
  assertError(await send(origin, { headers: { 'idempotency-key': 'invalid key with spaces' } }), 400, 'invalid_idempotency_key');
});

test('authentication adapter failure/deadline fails closed without exposing diagnostics', async (t) => {
  const origin = await start(t, { authenticate: () => { throw new Error('internal-adapter-diagnostic'); } });
  const result = await send(origin);
  assertError(result, 503, 'auth_unavailable');
  assert.equal(JSON.stringify(result.body).includes('internal-adapter-diagnostic'), false);
  let signal;
  const timeoutOrigin = await start(t, {
    authTimeoutMs: 20,
    authenticate: (_, options) => { signal = options.signal; return new Promise(() => {}); },
  });
  assertError(await send(timeoutOrigin), 503, 'auth_unavailable');
  assert.equal(signal.aborted, true);
});

test('unexpected service adapter failure produces a non-leaking correlated error', async (t) => {
  const origin = await start(t, { newId: () => { throw new Error('internal-data-adapter-diagnostic'); } });
  const result = await send(origin);
  assertError(result, 500, 'internal_error');
  assert.equal(JSON.stringify(result.body).includes('internal-data-adapter-diagnostic'), false);
});

test('bounded store still replays an existing receipt but refuses additional records', async (t) => {
  const origin = await start(t, { maxRecords: 1 });
  const original = await send(origin, { key: 'first' });
  const replay = await send(origin, { key: 'first' });
  assert.equal(replay.response.status, 201);
  assert.deepEqual(replay.body, original.body);
  assertError(await send(origin, { key: 'second' }), 503, 'capacity_reached');
});

test('streamed requests without Content-Length enforce the cumulative byte limit', async (t) => {
  const origin = await start(t);
  const body = Readable.from(Array.from({ length: 6 }, () => Buffer.alloc(1024, 0x78)));
  const result = await send(origin, { body, duplex: 'half' });
  assertError(result, 413, 'payload_too_large');
});
