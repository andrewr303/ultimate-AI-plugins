---
name: pds-campaign
description: "Use when defining a product-video campaign angle, audience, awareness stage, placement, CTA or bounded paid-social matrix with genuinely different test hypotheses."
---

# Campaign direction and variants

Read [campaign](../../references/campaign.md) and the evidence ledger. Paid social needs an explicit audience and experiment design.

1. State who should care, what they know, the problem/opportunity, main promise, proof action, resulting benefit, CTA and placement. Do not invent an offer or business outcome.
2. Choose an evidence-backed angle: direct workflow, problem/action, before/after, feature reveal, continuous transformation, narrated sample scenario or music-led launch.
3. Write distinct hook hypotheses and materially different bodies. Change the reason to care or proof emphasis; a color swap is not a marketing test.
4. Record audience, awareness, pain/outcome, hook, proof, offer if supplied, CTA, duration, placement and tested variable in campaign/experiment manifests.
5. Run `python scripts/studio.py campaign --brief BRIEF.json --output CAMPAIGN --hooks 3 --bodies 2 --ratios 9:16,16:9 --max-variants 12` for a bounded matrix. A smaller set is valid.
6. Materialize selected jobs with `python scripts/variants.py --job JOB.json --manifest EXPERIMENTS.json --output NEW_JOBS --limit 6`. Use an absent or empty destination; existing campaign files are preserved. Changed duration with supplied or preserved audio requires a separately authored aligned job. Sound-off caption and review-point times scale together; verify product action timing in preview.
7. Render low-cost previews first. Recompose product, headline, captions, CTA and safe areas per ratio. Select finals by purpose and comprehension.

Consult bundled placement profiles and record source/verification dates. Separate technical upload requirements from creative defaults. Do not claim effectiveness without real campaign data.
