# Provenance and rights

The original material in this package is released under the MIT License (see [LICENSE](LICENSE)). That covers the skills, references, agent briefs, commands, templates, scripts, tests, the engine in `examples/glass-lab/liquid-glass.js` and the lab page.

## Supplied source archives

The user supplied five open-source liquid glass projects as ZIP archives. They were read as evidence. No file from them is redistributed here, and the engine was written from scratch rather than adapted. References quote short formulas (a few lines at most) with attribution from the projects that ship an MIT license text and copyright line, so a reader can check the claim against the upstream code. Code from `@ybouane/liquidglass` and from liquid-glass-react's `src/shader-utils.ts` is never quoted; references restate those formulas as math in our own notation, with a citation.

| Project (as supplied) | Version observed | License observed | Copyright line |
| --- | --- | --- | --- |
| Glass HQ `liquid-glass` (`@glass-sdk/liquid-glass`) | 0.0.2 | MIT | Copyright (c) 2026 Glass HQ |
| `simple-liquid-glass` | 5.7.0 | MIT | Copyright (c) 2025 lucaperullo |
| `liquidGL` (`liquid-gl`) | 3.0.0 | MIT | Copyright (c) NaughtyDuk |
| `@ybouane/liquidglass` | 1.0.3 | MIT in `package.json` and README; the archive has no LICENSE file | none present |
| `liquid-glass-react` | 1.1.1 | MIT | Copyright 2025 MAX ROVENSKY |

Third-party code inside those archives, recorded so nobody mistakes it for the host project's own work:

- `simple-liquid-glass` vendors code from samasante/liquid-glass (MIT, (c) 2026 Sam Asante), `@ybouane/liquidglass` 1.0.3 (MIT), html-to-image 1.11.11 (MIT) and parts of naughtyduk/liquidGL (MIT).
- `liquid-glass-react` marks `src/shader-utils.ts` as adapted from shuding/liquid-glass. That upstream license is not in the archive, so references paraphrase that file's formulas and quote none of its code.
- The Glass HQ native reference app bundles Hugeicons paths (MIT) and the Inter font (SIL OFL 1.1).

Because `@ybouane/liquidglass` ships no LICENSE file or copyright line, its ideas are described in our own words and notation, and none of its code is reproduced.

The source notes in `references/sources/` describe each project's technique and API with `path:line` citations into the upstream layout. Versions are the ones in the supplied archives and may not be the latest.

## Existing agent skills

`research/skills-survey/` records a survey of existing liquid glass agent skills carried out on 2026-11-05. Ideas adopted from it are re-implemented in original prose and code. Where an idea is specific enough to credit, the adoption map in [the decision report](research/skills-survey/outputs/research-decision-report.md) names its origin. Two projects (Tsdsj/Apple-Style and anubhavaanand/glass-of-web) had no license file at the inspected commit, so they are cited and nothing is copied from them.

## Platform facts

Apple, Liquid Glass, SwiftUI, UIKit and AppKit are trademarks of Apple Inc. This plugin is unaffiliated with Apple and contains no Apple assets. References quote a few short sentences and one-line API examples from Apple's public documentation and Human Interface Guidelines, each with its URL and check date, and list API declaration signatures as interface facts. No Apple sample project or longer documentation text is reproduced. "Liquid glass style" describes a family of visual techniques; Apple's material is called Liquid Glass. Platform facts in `references/research-snapshot.md` cite public sources with the date they were checked. License labels in this file and in the research records are observations, not legal advice.
