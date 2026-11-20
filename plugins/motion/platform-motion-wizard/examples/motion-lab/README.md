# Local interaction lab

Open `index.html` directly in a current browser, or serve this directory using
an existing local development server. From the plugin root, Python's
standard-library option is:

```sh
python -m http.server 8765 --bind 127.0.0.1 --directory examples/motion-lab
```

Then open `http://127.0.0.1:8765`. The page has no external requests, runtime
dependencies, analytics, persistence, audio, or real service operations.
`motion-lifecycle.js` provides an original presentation controller and live
motion policy; `lab.js` owns this example's semantic state and controls. Both
are classic scripts and need no module fetching. Managed browsers may block
local-file navigation; use the local server in that case. Direct file loading
was attempted in the authoring environment but blocked by Chromium policy.

## Try these comparisons

1. Activate **Save example** with pointer, Space, and Enter. Selection changes
   immediately while visual feedback accompanies it.
2. Open the native dialog, replay its entry, press Escape, and reopen it.
   Check first-frame interaction, focus placement, and focus return.
3. Set **Detail illustration** to its longest duration. Open, close, and reopen
   the details while the bar moves. The bar retargets from its current visible
   position. Expanded state and content availability change immediately;
   closing from the internal button returns focus before hiding the content.
4. Start a simulation with **Failure**, then start a newer one with **Success**.
   Choose **Deliver latest**, then **Deliver oldest**. The old failure is
   actually received and counted as ignored; it cannot overwrite the newer
   success. Start again, cancel, and deliver its response. The canceled intent
   remains canceled even though its response arrives.
5. Turn on **Use no motion** while the bar is moving. Repeat each operation.
   A live system reduced-motion change also settles the latest visual endpoint.
   The comparison setting can only reduce motion further; it cannot override
   the system preference. Only effects owned by this example's controllers
   are canceled.
6. Repeat at a narrow viewport, with dark appearance, with right-to-left
   document direction, and with keyboard only.

The simulation is a bounded manual delivery queue. It sends no network request,
uses no response timer, and does not demonstrate transport/server cancellation.
At most eight responses can be queued. Delivering one releases queue capacity;
only six recent deliveries are retained in the log. Leaving the page clears
the local fixture and releases presentation resources. Returning recreates
the presentation policy; actual browser cache restoration still needs
product-specific verification.

The native dialog closes immediately. The details content also hides
immediately; its separate bar is decorative, accessibility-hidden, and inert.
Neither example attaches focus, semantic visibility, business success, or
request confirmation to animation completion. When WAAPI is unavailable,
both use the same stable endpoints immediately. These examples illustrate
ownership contracts; they are not a replacement for production overlay or
disclosure primitives.

The durations are original tuning examples, not measurements of Apple software
or universal values. This small page does not verify your application's
actual stack, assistive technology, layout, backend, native platform, or
performance. Review the product itself after using the lab.

## Browser checks

In an environment with Playwright and Chromium already installed, run from the
plugin root:

```sh
python tests/check_lab.py --output /absolute/path/outside-the-plugin
```

The script installs nothing. `--browser` selects an existing Chromium
executable; `--no-sandbox` is available for an isolated container that
requires it. Evidence includes the browser version, completed check groups,
sampled retarget progress, and stable desktop/narrow screenshots. The checks
cover real delivered stale/canceled responses, active motion before live
reduction, unrelated effect preservation, missing-WAAPI fallback, direct
file loading (recorded as skipped if browser administration policy blocks it),
keyboard/focus, queue bounds, and HTTP request isolation.
They do not establish physical-device, assistive-technology, native-platform,
frame-rate, or real back-forward cache behavior.
