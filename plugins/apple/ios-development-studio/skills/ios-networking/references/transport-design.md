# Transport design

Start from an actual endpoint contract and the existing architecture. Keep request construction, execution, validation, decoding and domain mapping distinct where that creates useful seams. A single tiny app does not need a framework of repositories and generic endpoint types; a larger client should not duplicate auth/error/retry logic in each view.

## Request construction and HTTP results

Build URLs with URLComponents and validated path/query values. Preserve the configured base URL and environment. Do not concatenate unescaped user input or put credentials in query strings. Set method, headers and body deliberately, including Content-Type and expected Accept values where the service requires them. Do not invent endpoint names or schemas from UI copy.

URLSession coordinates transfers; URLRequest describes a request. A transport success still needs HTTP validation. Cast the response to HTTPURLResponse, accept the service's documented success statuses and decode the body appropriate to that status. An empty successful response must not be fed through a decoder that requires an object. Error bodies may have a separate schema; preserve an actionable domain error without surfacing raw sensitive server data.

Check content size and transfer type. Data tasks suit bounded interactive responses. Use file download/upload APIs when the body is large or background transfer is actually required. A foreground Task is not an iOS background transfer guarantee. Streaming needs a cancellation-aware consumer and a bounded buffering policy.

## Isolation and ownership

Use a clear actor/isolation boundary for mutable auth, request state and caches. Immutable Sendable request/response models can cross boundaries. URLSession async methods suspend the caller; they do not prove that every later decode or transformation runs away from the main actor. Inspect Swift language mode, default actor isolation and compiler behavior before moving heavy CPU work. Do not add Task.detached or unchecked Sendable to silence a diagnostic without understanding captured state.

Keep transport work out of SwiftUI body evaluation. View-driven fetches should normally follow an explicit task identity, and store-owned operations should have a documented lifetime. Propagate cancellation through the awaited call and retry sleeps. Before publishing results, ensure the request generation/account still matches the recipient. Do not swallow cancellation as a generic failure.

## Session configuration

Choose default, ephemeral or background sessions for actual requirements. Apple's URLSession documentation states ephemeral sessions avoid writing caches, cookies and credentials to disk; that choice alone is not a complete privacy guarantee for the app's own logging or persistence. Set reasonable request/resource timeout and connectivity behavior for the product. Understand whether redirects may cross hosts before attaching sensitive headers.

A URLSession retains its delegate until invalidation; manage service/session lifetime intentionally when using delegates. Do not create a new session per row or leak a cycle through callbacks. Follow the real package API when an existing networking client wraps URLSession.

## Errors, logs and metrics

Distinguish cancellation, transport errors, HTTP failures, decode/contract failures and domain rejection. Map them to recovery that the user can perform. Avoid a blanket 'no internet' message for authorization failures or malformed responses. Log route templates, status classes, duration and a safe correlation identifier; redact headers, tokens, personal body fields and signed URL queries.

Measure request count and latency only with defined start/end points. Connection reuse, server cache behavior and simulator networking can affect observations. Never claim an optimization from a reduced line count.

## Sources

Original guidance informed by inspected official Apple references: [URLSession](https://developer.apple.com/documentation/foundation/urlsession), [URLRequest](https://developer.apple.com/documentation/foundation/urlrequest), [URLCache](https://developer.apple.com/documentation/foundation/urlcache), and the uploaded Nuke pipeline's separation of loading/caching/UI responsibilities. No upstream network implementation is copied. See [source map](../../../docs/source-map.md). Use current SDK declarations for exact API availability.
