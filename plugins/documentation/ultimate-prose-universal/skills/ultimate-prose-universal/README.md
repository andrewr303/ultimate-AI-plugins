# Ultimate Prose 5.2.0

Write, edit, review, or co-write prose in the tone you request. Start with plain/direct, warm, analytical, bold, playful, expert, or any custom blend. No personal profile or sample corpus is bundled. Optional calibration uses your own relevant examples.

Try: "Make this warm but firm; keep the refusal clear," "Review this essay and leave it untouched," or "Interview me, then help me write a post about why our design reviews stopped working." The skill fixes substance before surface: it asks what the piece owes its reader, marks missing facts as `[TK: question]` instead of inventing them, and restores image, stance, or warmth that cuts removed. Existing effective voice survives a light edit. The skill does not guarantee an authorship or detector result.

Import this directory through a compatible host, or copy it into the host's documented skill location. Install one copy, and avoid installing it beside another skill named `ultimate-prose`, because hosts may expose duplicates or pick the wrong one.

Python is optional. From this directory:

```sh
python scripts/lint.py draft.txt --genre email --tone warm
python scripts/prose_stats.py draft.md --compare earlier.md
python scripts/fidelity_check.py source.txt rewrite.txt
python scripts/fidelity_check.py source.txt summary.txt --mode summary
python scripts/lint.py draft.txt --avoid "delve, tapestry" --straight-quotes --no-em-dash --strict
python scripts/validate_package.py --release
python -m unittest discover -s tests -v
```

The tools use the standard library, read local text, and never rewrite or transmit it. Scanner findings are contextual REVIEW candidates; `prose_stats.py` reports descriptive measurements and look-here lists with no score; `fidelity_check.py` lists anchors a rewrite dropped or added, including new promises and causes, and `--mode summary` lists additions only for a requested cut. Typography and avoid-term conventions are off unless selected, and strict mode exits 1 only for selected convention findings (or, in `fidelity_check.py`, a changed hard anchor). Exit 2 means an input or usage error. `--detect` is an editorial-report alias, never an authorship detector.

Small English pattern checks and heuristic source masks cannot establish truth, meaning preservation, tone fit, quality, or origin. Review findings in context. If Python is unavailable, use the editorial workflow manually.

Version 5.2.0 adds `references/preservation.md` (what must survive an edit, claims and gaps, and the habits a fix must not create), more pattern rows with their weight, reply and first-contact guidance, a fuller voice card, new scanner constructions for staged contrast, objections nobody raised, and draft artifacts, and twelve behavioral cases. The ideas come from five supplied projects credited in `NOTICE.md`.

See `references/tones.md` for presets and blends, `references/review.md` and `references/interview.md` for the review and co-write modes, `references/voice-calibration.md` for optional personal use, `references/research.md` for sources, `references/validation.md` for what was checked in this release, and `NOTICE.md` for Clarity's MIT license.
