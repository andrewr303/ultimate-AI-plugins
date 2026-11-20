---
name: mps-delivery
description: "Use when packaging a completed product marketing site with runnable source, preview commands, optimized assets, QA evidence and a self-contained capture or video handoff."
---

# Marketing site delivery

Read [delivery](../../references/delivery.md). Finish authorized implementation and repair before presenting the result.

1. Run package checks from the installed plugin and applicable site checks. Start the delivered source using the documented command, without the development checkout or original archives.
2. Include homepage and useful supporting routes, responsive assets, local fonts or documented fallbacks, dependency lockfiles where applicable and readable preview instructions.
3. Include a product brief, brand/evidence/capture/rights manifests, assumptions and source-bound QA report. Record unsupported claims that were omitted and material remaining limitations.
4. Validate the self-contained handoff, then use `python scripts/studio.py handoff --from-dir PROJECT --output HANDOFF`. Check all copied files and hashes. Product Demo Studio is optional for consuming the captures.
5. For incoming video assets, preserve mode, rights, poster, captions, dimensions and source/configuration hashes. Use muted inline playback only when appropriate; expose controls/alternatives and avoid blocking page comprehension.
6. Deliver concise links to source, preview instructions and key evidence. Deployment, publication and external uploads happen only when requested.

Keep generated footage, private auth, caches and scratch assets out of the site source package. Do not call the site production-ready while known critical keyboard, claim or rendering defects remain.
