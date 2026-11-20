# Deterministic UI motion and camera

Technique lineage: pure frame composition and measured targeting from Agentic Product Demo; seek-based springs/connected transforms from current Product Launch Motion; separate camera nodes and narration alignment from its legacy track; source-aware framing from Product Demo Director. These are techniques, not fixed visual rules.

## Pure playhead

The same source/configuration at time t must produce the same frame regardless of prior seeks. Use named events and interpolation. Disable uncontrolled transitions, timers, unseeded randomness and network content in controlled scenes. Actual footage retains source timing and is not a reconstructed UI.

Initialize animated properties on every seek. Prior `display:none`, opacity/filter/transform or hidden classes must not leak. Test seeking later -> earlier -> later.

## Vocabulary

- Ramps: clamped normalized progress and easing for travel.
- Damped springs: deterministic landing/size/position responses with little/no overshoot for text/camera.
- Stagger: short offsets for list arrivals while preserving total reading time.
- Press: bounded response after cursor arrival.
- Typing: visible prefix derived from verified text and playhead; no implied live call.
- Counters: sourced/sample values in their declared scope, never fabricated business metrics.
- Visibility windows: separate incoming/outgoing timing to avoid text overlap during morphs.

Interpolate status/color when continuity helps. Keep font weights/layout stepped where interpolation reflows glyphs. A direct state change can be correct; the purpose is legibility and causality.

## Coordinates and cursor

Separate product coordinates, camera and screen overlays. Put independent scale/rotation on separate nodes. Cursor and target share a coordinate space or an exact transform. Measure rendered bounds rather than estimating padding.

Use arrival, press-spanning hold and departure keys. A lone arrival key can start departure before the click. During drag, derive manipulated value from cursor position while held, then settle after release.

## Camera and text

Use motion to connect action/result or reveal relevant scale. Retain context, status and consequences. Arrive before reading. Inspect rasterized glyphs at maximum zoom: a large source and HD export do not prove sharp text. A complete native detail plate can explain better than a dense dashboard.

Avoid a permanent transform on the whole UI merely to fit it; recompose or render appropriate geometry. Test compositor and will-change choices in the actual output because they can blur text.

Connected transformations are optional. Animate a logical surface's bounds/radius, separately timing old/new content, when continuity helps the story. Do not force every film into one morphing shape.

## Loops and review

A seamless loop matches first/last visual, camera, cursor, velocity and audio boundary. Compare boundary frames and repeat playback. Inspect opening, press, processing, arrival, settled result, transitions and close. Measure cursor alignment in output and inspect native sharpness/caption bounds. Watch normal-speed encoded motion for shimmer and rushed holds; stills cannot prove pacing.
