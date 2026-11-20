# Campaign strategy and purposeful variants

## Campaign brief

Record audience/buyer, awareness, known context, pain/opportunity, single promise, demonstrating action, benefit, CTA, placement, duration and constraints. Link promise to claim IDs. Offers must be supplied or verified.

Choose from direct workflow, problem/action, comparable before/after, focused reveal, continuous transformation, narrated sample scenario or music-led film. Each still requires meaningful product action. A paid viewer may lack context supplied by an organic post; make relevance and product meaning self-contained.

## Experiment matrix

| Field | Purpose |
| --- | --- |
| Audience and awareness | Defines whose situation the hook recognizes and explanation needed |
| Pain/outcome | Gives a reason to care |
| Hook | States the opening hypothesis |
| Main proof | Identifies actual action/result |
| Offer and CTA | Records supplied proposition and next action |
| Duration and placement | Bounds proof, reading time and native composition |
| Tested variable | Distinguishes a hypothesis from decoration |

A bounded default is three hooks, two bodies and two ratios, capped at twelve variants. A smaller set can answer the request better. Preview first; do not automatically render a full matrix.

Tandem sample hypotheses:

- Problem recognition: "A full inbox is not a priority list." Tests whether recognized pain leads the story.
- Direct proof: "Watch sample requests become a reviewable queue." Tests whether action explains value faster.
- Control/trust: "Suggested groups. Your final call." Tests whether edit/reorder control answers an automation objection.

Bodies can follow one request to result versus show sorting/inspecting/editing a queue. These are scenario hypotheses, not measured performance claims. A new accent color is not a new audience insight.

## Native placement

Vertical needs a short reading axis, one complete product unit and reserved caption/CTA space. Landscape can retain context beside detail. Square/portrait feed need their own spacing. Never center-crop away the action or labels.

Use editable profiles and official sources for platform-specific upload rules. Record URL and verification date. Keep creative safe-area recommendations distinct; device overlays vary. Use stable variant IDs connecting campaign, hook, body, ratio, CTA and hypothesis to artifact paths/hashes/review. Do not name a winner without distribution data.

## Materializing jobs safely

Run `python scripts/variants.py --job JOB.json --manifest EXPERIMENTS.json --output NEW_JOBS --limit 6` to create a bounded set of independent render jobs. The destination must be absent or empty, differ from the source project, and have no symlink path components. The compiler resolves all referenced inputs and checks asset/job/manifest filename collisions before staging output. It publishes the completed project after copies succeed; an interrupted copy leaves the destination absent or empty. Existing campaign files are never overwritten. Use a new destination for another materialization.

Unchanged-duration variants preserve supplied audio and caption timings. For sound-off jobs, changed durations scale caption and authored review-point times together. A duration change with any supplied audio or preserved source audio fails: author a separate job with aligned speech, cues, captions and review points before varying its duration. The compiler does not stretch audio or claim to align speech. Existing configuration hashes are recomputed for each generated job. Inspect native layouts and proof timing in representative previews before final production.
