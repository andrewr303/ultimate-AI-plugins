# Source and provenance notice

Ultimate Prose declares `license: MIT` in its frontmatter. The supplied archives contain no separate license text or copyright line for the skill itself, and this notice does not invent an author or represent an independent rights clearance.

## Third-party material: Clarity

Portions of `scripts/prose_stats.py` and `scripts/validate_package.py`, the behavior categories and several cases in `references/test-cases.json`, the judging protocol, the review verdict format, the interview procedure, the long-form craft guidance, and the medium routing table are adapted from Clarity (github.com/addyosmani/clarity), supplied to this revision as `clarity-main.zip` with `SKILL.md` metadata version 0.2.1. The adaptations were rewritten for this skill; where code or case text follows the original closely, it remains under Clarity's license:

```text
MIT License

Copyright (c) 2026 Addy Osmani

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Supplied tells catalog

Several pattern entries (demonstrative kicker, meta throat-clearing, importance-flagging, decorative metaphor, the plainer-word lexicon, the five triage questions, and touch calibration) adapt a user-supplied `tells.md` that states no author or license. Its examples were shortened or paraphrased, and no license or ownership is asserted for that file here.

## Version 4.4.0 sources

Version 4.4.0 merges ideas from five further archives Andrew supplied. The guidance, examples, scanner rules, and tests added for it were written fresh; no source file is bundled, and every example is synthetic. Some short items were adapted closely enough that their authors are credited here: families of phrases the scanner looks for, marker families the fidelity check counts, and a small number of detection ideas. Each license below asks that its copyright notice travel with substantial portions, under the same MIT permission text reproduced above for Clarity.

| Source (version in the supplied archive) | License and notice |
|---|---|
| [plainspoken](https://github.com/littlebearapps/plainspoken) 0.13.0 | MIT. Copyright (c) 2026 Little Bear Apps |
| [humanizer](https://github.com/blader/humanizer) 4.0.0 | MIT. Copyright (c) 2025 Siqi Chen |
| [avoid-ai-writing](https://github.com/conorbronsdon/avoid-ai-writing) 3.39.0 | MIT. Copyright (c) 2026 Conor Bronsdon |
| writing-quality 0.2.3 (bundles an "unslop engine") | MIT. Copyright (c) 2026 Contributors. Its own notices credit humanizer, [stop-slop](https://github.com/hardikpandya/stop-slop) (Copyright (c) 2025 Hardik Pandya), [no-ai-slop](https://github.com/petergyang/no-ai-slop) (Copyright (c) 2026 Peter Yang), and avoid-ai-writing |
| unslop 2.3.0 | Declared `license: MIT`, author `claytonkim`, in its skill metadata. The archive contains no license file or copyright line |

Several of these projects draw on Wikipedia's "Signs of AI writing" page, which is licensed CC BY-SA 4.0. This package describes the same kinds of habits in its own words and does not reproduce that page's text or examples. The licenses were read from the supplied archives only; no independent rights clearance was performed. `references/validation.md` records what was taken from each source and what was left out.
