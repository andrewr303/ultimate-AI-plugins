# Documentation quality bar

Use judgment rather than a decorative checklist. A short, accurate README may need no image; a complex service may need an architecture diagram and several task guides.

| Dimension | Acceptance evidence | Common failure |
| --- | --- | --- |
| Factual accuracy | Trace statements to code, tests, schema or maintained config | Invented flags, unsupported compatibility |
| First success | Prerequisites, exact commands, expected output, next step | A command wall with no outcome |
| Information architecture | Reader tasks, meaningful titles, reachable pages | Sidebar mirrors internal folders without helping readers |
| Visual hierarchy | Clear opening, restrained accent, consistent type/spacing | Badge walls, giant hero before useful content |
| Code readability | Language labels, safe copyable examples, controlled overflow | Screenshots of code, invisible selection, mixed prompts/output |
| Accessibility | Semantic headings, descriptive links/alt, keyboard focus, text equivalents | Meaning conveyed only by color or image |
| Rendering | Actual GitHub or framework output checked | MDX pasted into a README, unsupported Mermaid syntax |
| Maintainability | Generated sources, owners and update triggers clear | Duplicated API tables that drift |

For websites, use the project's established tokens. A new direction may use a restrained neutral background, one functional accent, strong code contrast and a deliberate spacing scale. Aim for a readable prose measure around 65–80 characters; inspect actual layout rather than forcing one width everywhere. Tables and code may need controlled horizontal scrolling on phones.

Check normal text contrast against WCAG AA targets (4.5:1, or 3:1 for qualifying large text), visible focus, meaningful labels and headings. These targets are review criteria, not a claim of compliance. Automated accessibility checks complement manual keyboard, reading order and viewport checks.

Inspect at least a narrow phone view and a typical desktop view, and include dark mode when supported. Exercise search loading/empty/error/results, mobile navigation, code copy status, tabs and disclosures when present. Honor reduced motion; avoid animated decoration that competes with reading.

README-specific: GitHub controls typography and theme; use clear text structure, small honest badge groups, concise comparison tables, supported callouts and useful images. Do not promise external fonts, custom CSS, JavaScript widgets or precise card layouts on GitHub.

Treat "beautiful" as clear hierarchy and useful content. More components do not establish higher quality.
