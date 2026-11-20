// Reusable framing primitive, not a complete native messaging host.
// Node built-ins only. Byte order is the executing host's native byte order.
import { endianness } from 'node:os';
import { TextDecoder } from 'node:util';

const littleEndian = endianness() === 'LE';
export const DEFAULT_MAX_BYTES = 1024 * 1024;
const ABSOLUTE_MAX_BYTES = 64 * 1024 * 1024;

function checkedLimit(limit) {
  if (!Number.isInteger(limit) || limit < 1 || limit > ABSOLUTE_MAX_BYTES) {
    throw new RangeError('maxBytes must be an integer from 1 through 64 MiB');
  }
  return limit;
}

function requireObject(value) {
  if (value === null || typeof value !== 'object' || Array.isArray(value)) {
    throw new TypeError('application messages must be JSON objects');
  }
  return value;
}

export function encodeFrame(message, maxBytes = DEFAULT_MAX_BYTES) {
  checkedLimit(maxBytes);
  if (maxBytes > DEFAULT_MAX_BYTES) {
    throw new RangeError('host-to-Chrome frames must not exceed 1 MiB');
  }
  const serialized = JSON.stringify(requireObject(message));
  // toJSON can change the top-level shape, so check the actual encoded value.
  requireObject(JSON.parse(serialized));
  const body = Buffer.from(serialized, 'utf8');
  if (body.length < 1 || body.length > maxBytes) {
    throw new RangeError('serialized message exceeds configured byte limit');
  }
  const header = Buffer.alloc(4);
  if (littleEndian) header.writeUInt32LE(body.length);
  else header.writeUInt32BE(body.length);
  return Buffer.concat([header, body]);
}

export class FrameDecoder {
  constructor(maxBytes = DEFAULT_MAX_BYTES) {
    this.maxBytes = checkedLimit(maxBytes);
    this.header = Buffer.alloc(4);
    this.headerUsed = 0;
    this.body = null;
    this.bodyUsed = 0;
    this.closed = false;
    this.utf8 = new TextDecoder('utf-8', { fatal: true, ignoreBOM: true });
  }

  push(chunk) {
    if (this.closed) throw new Error('decoder is closed');
    if (!Buffer.isBuffer(chunk)) throw new TypeError('expected Buffer');
    const messages = [];
    let offset = 0;
    try {
      while (offset < chunk.length) {
        if (this.body === null) {
          const count = Math.min(4 - this.headerUsed, chunk.length - offset);
          chunk.copy(this.header, this.headerUsed, offset, offset + count);
          this.headerUsed += count;
          offset += count;
          if (this.headerUsed < 4) continue;
          const length = littleEndian ? this.header.readUInt32LE() : this.header.readUInt32BE();
          if (length < 1 || length > this.maxBytes) {
            throw new RangeError('invalid or oversized frame length');
          }
          this.body = Buffer.allocUnsafe(length);
          this.bodyUsed = 0;
        }
        const count = Math.min(this.body.length - this.bodyUsed, chunk.length - offset);
        chunk.copy(this.body, this.bodyUsed, offset, offset + count);
        this.bodyUsed += count;
        offset += count;
        if (this.bodyUsed === this.body.length) {
          messages.push(requireObject(JSON.parse(this.utf8.decode(this.body))));
          this.body = null;
          this.bodyUsed = 0;
          this.headerUsed = 0;
        }
      }
      return messages;
    } catch (error) {
      this.closed = true;
      this.body = null;
      throw error;
    }
  }

  finish() {
    if (this.closed) throw new Error('decoder is closed');
    this.closed = true;
    if (this.headerUsed !== 0 || this.body !== null) {
      this.body = null;
      throw new Error('truncated native messaging frame');
    }
  }
}
