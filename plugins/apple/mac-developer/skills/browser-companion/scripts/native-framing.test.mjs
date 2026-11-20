import test from 'node:test';
import assert from 'node:assert/strict';
import { endianness } from 'node:os';
import { encodeFrame, FrameDecoder } from './native-framing.mjs';

function rawFrame(body) {
  const header = Buffer.alloc(4);
  if (endianness() === 'LE') header.writeUInt32LE(body.length);
  else header.writeUInt32BE(body.length);
  return Buffer.concat([header, body]);
}

test('UTF-8 byte length and native-endian prefix round trip', () => {
  const message = { type: 'hello', title: '截图 🖥️ café' };
  const encoded = encodeFrame(message);
  const length = endianness() === 'LE' ? encoded.readUInt32LE() : encoded.readUInt32BE();
  assert.equal(length, Buffer.byteLength(JSON.stringify(message)));
  const decoder = new FrameDecoder();
  assert.deepEqual(decoder.push(encoded), [message]);
  decoder.finish();
});

test('every split boundary, concatenated frames, and bytewise input', () => {
  const expected = [{ type: 'one', title: '🌄' }, { type: 'two', sequence: 2 }];
  const bytes = Buffer.concat(expected.map(message => encodeFrame(message)));
  for (let split = 0; split <= bytes.length; split++) {
    const decoder = new FrameDecoder();
    assert.deepEqual([...decoder.push(bytes.subarray(0, split)), ...decoder.push(bytes.subarray(split))], expected);
    decoder.finish();
  }
  const decoder = new FrameDecoder();
  assert.deepEqual([...bytes].flatMap(byte => decoder.push(Buffer.from([byte]))), expected);
  decoder.finish();
});

test('rejects zero and oversized lengths as soon as header is complete', () => {
  for (const length of [0, 129, 0xffffffff]) {
    const header = Buffer.alloc(4);
    if (endianness() === 'LE') header.writeUInt32LE(length);
    else header.writeUInt32BE(length);
    const decoder = new FrameDecoder(128);
    assert.throws(() => decoder.push(header), /frame length/);
    assert.throws(() => decoder.push(Buffer.alloc(0)), /closed/);
  }
});

test('rejects malformed UTF-8, JSON, BOM, and wrong application shape', () => {
  for (const body of [Buffer.from([0xff]), Buffer.from('{bad}'), Buffer.from('\uFEFF{}'), Buffer.from('null'), Buffer.from('[]')]) {
    assert.throws(() => new FrameDecoder().push(rawFrame(body)));
  }
});

test('rejects truncated headers and payloads on EOF', () => {
  const bytes = encodeFrame({ type: 'ack', requestId: 'a' });
  for (let end = 1; end < bytes.length; end++) {
    const decoder = new FrameDecoder();
    decoder.push(bytes.subarray(0, end));
    assert.throws(() => decoder.finish(), /truncated/);
  }
  new FrameDecoder().finish();
});

test('outbound limit uses bytes and checks toJSON output', () => {
  const message = { value: '🌄' };
  const exact = Buffer.byteLength(JSON.stringify(message));
  assert.doesNotThrow(() => encodeFrame(message, exact));
  assert.throws(() => encodeFrame(message, exact - 1), /byte limit/);
  assert.throws(() => encodeFrame({ toJSON: () => [] }), /JSON objects/);
  assert.throws(() => encodeFrame(null), /JSON objects/);
  assert.throws(() => encodeFrame({}, 1024 * 1024 + 1), /host-to-Chrome/);
  for (const limit of [0, -1, 0.5, 64 * 1024 * 1024 + 1]) {
    assert.throws(() => new FrameDecoder(limit), /maxBytes/);
  }
});
