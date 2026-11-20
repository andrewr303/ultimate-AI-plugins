# Native messaging framing utility

`native-framing.mjs` is a dependency-free Node ESM primitive for the four-byte
native-endian length prefix and UTF-8 JSON. This application-level utility accepts
JSON objects only. Default inbound/outbound limit is 1 MiB; choose a lower negotiated
limit where useful. Chrome allows a larger extension-to-host limit, but raising
the decoder's limit requires a concrete product reason and resource bounds.
`encodeFrame` enforces a maximum 1 MiB response to Chrome even if the decoder's
inbound limit is larger. Serialized JSON overhead counts toward the limit.

Run its portable tests with:

```sh
node --test <skill-directory>/scripts/native-framing.test.mjs
```

Example, after substituting a real local module path:

```js
import { FrameDecoder, encodeFrame } from './native-framing.mjs';
const decoder = new FrameDecoder(512 * 1024);
// In a real host: decoder.push(buffer) for each stdin chunk; decoder.finish() on EOF.
// Validate each returned object with the agreed versioned application schema.
// Write encodeFrame(response) to stdout with backpressure; log only to stderr.
```

This file does not implement host registration, origin/peer validation,
authorization, app IPC, application schema validation, queues or storage. Those
are required by the browser-companion workflow. It never opens a socket or
starts a service. A passing codec test does not prove browser integration.

Use bounded chunk reads, serialized processing and stream backpressure in the
host. `push` returns all messages in one input chunk; bound the caller's chunk
and processing queues. Fail closed on parse errors; a decoder cannot be reused
after an error or EOF. Do not print messages or debug logs on native-host stdout.
