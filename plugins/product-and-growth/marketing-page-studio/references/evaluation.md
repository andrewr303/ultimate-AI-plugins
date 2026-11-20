# Ready prompts and behavior evaluations

These prompts are reusable tests, not evidence that an intended host executed a skill. The machine-readable [evaluation corpus](evaluation-prompts.json) records expected activation and behavior with `not-run` status. Keep actual results in a separate source-bound report and attach transcripts/output evidence when a host run is available.

## Ready-to-use requests

- “Build a homepage for this app with a working product demo in the hero.”
- “Redesign this marketing page around the actual interface.”
- “Make this workflow understandable through a scroll-controlled demonstration.”
- “Turn this feature into a 20-second vertical product ad.”
- “Create three genuinely different hooks for this product demonstration.”
- “Produce a narrated walkthrough using only verified product behavior.”
- “Create a seamless homepage loop from these interface states.”

Supply the repository, local app URL or verified captures when available; the studios discover context before asking questions. For standalone video requests route to Product Demo Studio; live website requests route to Marketing Page Studio. A combined campaign can use explicit file handoffs while each plugin operates independently.

## Evaluation protocol

1. Install from the packaged artifact into an isolated clean location using [installation guidance](../docs/INSTALL.md).
2. Invoke the entry skill through the intended host with a representative prompt and inspect whether relevant specialists/resources are loaded on demand.
3. Check observable output and behavior against the corpus: correct routing, source/claim handling, implemented states, complete production and precise dependency errors.
4. Run the actual delivered source/capture/render and inspect its browser/media evidence. Script execution alone cannot establish host activation or instruction-following.
5. Record host/version, source/artifact hashes, prompt, status, output paths and material limitations. Keep unavailable integrations `blocked`/`not-run`; never infer passes from prose.

## Required coverage

Homepage from repository; redesign in existing stack; screenshots-only page; offline deterministic AI sample; feature/workflow page; reduced motion/low JavaScript; organic launch/vertical ad; bounded paid pack; faithful narrated walkthrough; music-led transformation; missing evidence; missing browser/renderer; unrelated request that should activate neither. Also test stale previews after source changes.

## Review boundaries

Static frontmatter/link/package checks, clean installation, helper-script tests, actual browser observations, encoded-media checks, visual/editorial inspection and intended-host primary-skill execution are separate results. A prompt corpus establishes test design only. Keep claims about quality and compatibility within what was observed.
