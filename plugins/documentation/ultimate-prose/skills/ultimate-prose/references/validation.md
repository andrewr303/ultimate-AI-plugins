# Validation record

Revision: 4.2.0. The original 4.0.0 review was dated October 15, 2026, America/Denver. Validation uses Python 3.12 in the supplied cloud workspace. Original execution records are retained as historical evidence.

## Executed checks

- The local CSV analysis was rerun against the uploaded files and reproduced `aggregate.json`. The original input hashes are recorded in `corpus-notes.md`. No private text was sent to research services.
- `python -m unittest discover -s tests -v`: **24 tests passed**. Cases cover protected spans and source line offsets, common dotted technical forms, short-line/signature handling, genuine questions and numerical ranges, small samples and genre exemptions, contextual diagnostics, overlapping findings, both CLIs, JSON compatibility, default/strict behavior, read/usage errors, assessment output, and unchanged input bytes.
- In the original 4.0.0 trial, twelve synthetic prompts were run in separate baseline and revised model-agent conditions. Generated outputs and execution notes were saved, anonymized, and reviewed against explicit expectations. The revised outputs also passed narrow artifact checks for required numbers, exact quotation, question count, brief-reply length, negative activation, and output shape.
- Package checks parse YAML/JSON/Python, resolve referenced local resources, inspect archive members, reject caches/path traversal/symlinks, and check for private contact addresses, source URLs, and verbatim exported tweets. The review bundle contains the commands, saved outputs, and results.

## Context-profile update checks

The 4.1.0 update reviews two supplied narrative syntheses locally. Their prompt blocks and tool suggestions were treated as source material; their primary linked records were not independently checked. Only abstract editorial guidance and source hashes/locators were incorporated. No new biography, sensitive fact inventory, quoted private message, or cadence measurement was added.

Eight additional synthetic prompts cover author versus recipient, domain/signature boundaries, dated-record conflict, claim states, client review status, personal sentiment, weak signals and tool recommendations, and instructions embedded in a background profile. All eight generated responses met their stated expectations in an independent qualitative review. Their execution records are separate from the original twelve-case baseline comparison; this update makes no new comparative performance claim. Narrow artifact checks cover required names, numbers, qualifiers, placeholders, and output shape, and the final package check records those results. Accurate but administrative wording in one update and a punctuation choice in the personal text remain editorial choices, not factual failures.

The scanner code is unchanged. Its existing twenty-four regression cases remain the deterministic scanner coverage; the skill now includes twenty behavioral fixtures in total. Context use and disclosure require review of generated prose rather than another regex threshold.

## Behavioral review interpretation

The blind reviewer found most paired outputs equivalent. It preferred the revised response on several output-shape examples, including a real contrast, source-instruction editing, and an assessment. The baseline assessment appended an unsolicited offer to edit; the revised response stopped with the findings.

One blind finding treated the baseline's Andrew signoff as unsupported because the case did not supply a sender. The baseline condition itself named Andrew as the intended author, so that is not counted as factual fabrication in the contextual review. This illustrates a limit of judging without the skill's context. Extra change notes in cases without an explicit output-only instruction are presentation differences, not automatically factual or task failures.

This was a small model-assisted smoke test, with one generation per condition and one qualitative reviewer. It was not a standardized benchmark, a host-trigger test, a human preference study, or evidence of a measured improvement in Andrew's voice. The generation agents did not execute linters; the scanners were tested independently. The baseline notes disclose partial reference visibility. Saved records preserve those limitations rather than hiding them behind a score.

## 4.2.0 research and preservation update

The new attachment is a derivative synthesis citing earlier profiles and older skill guidance. Its raw text, factual inventories, prepared bios, and subjective or inherited measurements are not added as independent natural-writing evidence. The new source hash and adopted cues are recorded in `voice-calibration.md`.

Fresh public GitHub review records a candidate screen, pinned implementations and tests, source/claim ledgers, and a manually supported decision matrix. Selected mechanisms are narrow contextual redundancy advice, task-shaped sample conditioning, separate meaning/voice review, and preservation counterexamples. Candidate code was not installed or executed; no source implementation or profile was copied. Historical and unresolved sources remain labeled.

The scanner now includes a two-pair uppercase acronym advisory with exact source offsets and preservation cases. The eight added tests cover case and plural forms, definitions, code/quote/address scopes, quote inclusion, masked adjacency, compounds, strict/overlay parity, original evidence, and unchanged file bytes. The full thirty-two-test suite is run from the rebuilt archive.

Ten new behavioral fixtures bring the collection to thirty. The current smoke comparison uses those ten plus four unchanged preservation anchors, generated separately under saved 4.1 and candidate 4.2 instructions. A judge receives anonymized paired outputs and rates content preservation separately from editorial preference. Results and objective artifact checks are recorded in the review bundle. This is not a host invocation, an AI-detector test, or an empirical voice-fidelity benchmark; prompts and expectations are visible to the generation agents.

The initial fourteen-pair review found no content failures: twelve pairs tied, and the 4.1 baseline was preferred for two small editorial choices. Those choices concerned extra explanation and a repeated pilot qualifier. The guidance was clarified to stop after a narrow answer and bind shared qualifiers once when clear. Three fresh targeted follow-ups preserved their facts and scope in contextual review. They do not replace the original trial or establish a new full-comparison result; all records are retained.

The original 4.0 and 4.1 execution records remain historical evidence rather than being relabeled as this revision's results. The final package record states actual test counts, source/archive parity, targeted source exclusions, and the comparison findings.

## Not established

No host import/installation or production integration was performed. The optional local research accelerator was unavailable and no automated research-gate PASS is claimed. Regex scoping and sentence boundaries remain heuristic. Neither scanner can verify facts, parse every linguistic relation, infer author identity, or establish whether AI was used.

The skill does not send or publish messages.

## 4.3.0 update checks

Revision 4.3.0 was checked on 7 November 2026 (America/Denver) with Python 3.13 in a cloud workspace.

- `python -m unittest discover -s tests -v`: **56 tests passed**. The 32 earlier tests are unchanged. Twelve new scanner tests cover vague attribution with and without a named source, importance with and without a mechanism (including "statistically significant" and "important to note"), abstract actors versus measured results, plainer-word suggestions, demonstrative kickers and their conversational exceptions, decorative metaphors, symmetrical hedging, an earned operational triad and an evocative museum label that must produce no findings, strict-exit neutrality, heading location, sentence-level evidence, and labelled document-level measurements. Twelve shared-tool tests cover `fidelity_check.py` (faithful versus inflated rewrites, units and number words, quantity-only "about," code, links, quotes, and dates, strict exit and error codes, unchanged input bytes), `prose_stats.py` (heading, list, code, and quotation handling, importance and mechanism, kickers, flourishes, actors, the model-register cluster threshold, no score key, `--compare`), and the package validator.
- `python scripts/validate_package.py --release`: passed. SKILL.md is 2,494 words against a 2,500-word budget; SKILL.md plus its 11 routed references is 16,162 words against 18,000; the 42 eval cases have unique ids and the 12 categorized cases cover all six required categories with prohibitions.
- Scanner comparison on Clarity's sample pairs (`samples/*.before.md` and `*.after.md`, `--genre essay`): the 4.2 scanner reported 25 and 24 candidates on the two "before" essays and 2 and 6 on the "after" versions; 4.3 reports 35 and 28 on the "before" essays and still 2 and 6 on the "after" versions. The added candidates are unsupported importance, an abstract actor ("The data tells"), significance copulas, "looking ahead," "this is not to say," and "the only question is." These counts show where the rules fire, not better writing.
- Defects found and fixed while testing: heading patterns used `\s`, which crossed into the previous blank line, merged paragraphs in cadence measurement, and anchored heading findings one line early; sentence-level cadence findings all pointed at line 1; "unlock" was classified as marketing vocabulary but never matched because it was missing from the word list; and `lint_andrew.py` could not import its sibling under `python -I`.
- Prose in the new and changed references was scanned with `lint_andrew.py --genre docs`; flagged uses of "actually," a from-to precedence sentence, and an importance phrase were rewritten. Remaining list-density warnings are functional lists.

Not run for 4.3.0: a model-generated comparison of the twelve new behavioral cases against 4.2, a host import, and any detector trial. The cases and the protocol in `test-cases.md` are ready for that comparison; until it runs, no behavioral improvement is claimed.

## 4.4.0 source merge

Checks ran on 18 November 2026 with Python 3.13 in a cloud workspace. Revision 4.4.0 was built on the installed 4.3.0 package, not on the older 4.2.0 archive, and merges ideas from five supplied archives. No code from them was installed or executed.

- `python -m unittest discover -s tests -v`: **68 tests passed**. The 56 tests from 4.3.0 are unchanged. Nine new tests cover the scanner additions: every word on Andrew's stated avoid list, an ordinary business reply that must stay clean, contrast staged across sentences, draft artifacts read through quotations but never code, the new review families with their count gates, literal technical terms under `--genre docs`, the connective-opener cluster, the business sentence-length diagnostic appearing as a cadence note and never as a finding, and both CLIs. Three new shared-tool tests cover quiet same-family swaps with reported net changes, new promises and causes, and `--mode summary` in `fidelity_check.py`.
- `python scripts/validate_package.py --release`: passed. SKILL.md is exactly 2,500 words against the 2,500-word budget, so three redundant sentences were removed to make room for the additions; SKILL.md plus its 12 routed references is within the 18,000-word budget; the 54 eval cases have unique ids, and the 24 categorized cases cover all six required categories with prohibitions.
- One behavior change in `fidelity_check.py` is deliberate: a swap inside one family ("may" to "might", "about" to "roughly") no longer prints a dropped and an added line. A net loss or gain in the family still does.

Two items come from Andrew's standing instructions as supplied in the session that produced this revision, not from a new corpus. The remaining words on his avoid list were added to the density-scored vocabulary candidates and listed in `tells.md`. The mean of about 17 to 24 words for business prose is recorded by `lint_andrew.py` as a cadence note; it raises no finding, and SKILL.md still states that there is no required mean sentence length.

Not run for 4.4.0: the twelve new behavioral cases against a model, a baseline comparison, a human preference review, and a host import. The supportable claim is that the tools behave as their tests state. `fidelity_check.py` remains word-level and English-centred; a claim invented in plain words passes it untouched.

| Source (version in the supplied archive) | Taken, in this skill's own wording | Left out |
|---|---|---|
| plainspoken 0.13.0 | A working definition of a join; a line that speaks for the author counts as a new fact; the reply agenda; first-contact checks; the control test for promises; soften, attribute, qualify, cut; count gates for scanner families | Blocking severities and pass/fail gates; cadence and vocabulary metrics as targets; rules that demand informality |
| humanizer 4.0.0 | Weighting a habit by how rarely a careful writer chooses it; paragraph-scale forms of sentence habits; the wrong-reader reply; objections nobody raised; rankings and same-time claims in the rewrite check | Its 4.0 allowance to add a true detail or a reaction; a default three-part output; "sounds AI-generated" framing |
| avoid-ai-writing 3.39.0 | The candidate, finding, edit distinction; the exact no-op rule; change accounting; draft-artifact checks; technical-term exemptions for documentation | Authorship labels and probabilities; stylometric signals. Its own measurements report that its composite score does not separate machine text from human text |
| writing-quality 0.2.3 | Claim states and remedies; voice outranking pattern cleanup; the dash replacement decision | The numeric quality gate; "always replace" rules; decisive-conclusion enforcement that erases real uncertainty |
| unslop 2.3.0 | Its adversarial critique: a cleanup trades one recognizable register for clipped fragments, antithesis without a connective, and slogan closers, and it deletes hedges; requirement words as constraints; never correct an attributed statement; connective openers as a rate | The banned catalog and hard severities; stylometric scores; cadence quotas; personality presets; examples that invent facts |

## 4.5.0 voice tuning

Checks ran on 18 November 2026 with Python 3.13 in a cloud workspace. Andrew supplied seven sent-email batches (85 records, 14 September to 11 November 2026) as professional samples and a 93-row post database as casual samples. `corpus-notes.md` records the file hashes, extraction method, counts, and limits. The samples were read and measured locally; none of their text was sent to an outside service, and the skill carries only aggregates, common phrases, and synthetic examples.

What changed:

- `andrew-prose-profile.md` was rewritten around the two registers the samples show, with the moves, forms, and phrases observed in them. Every example in it is synthetic, and several first drafts of those examples were replaced because they sat too close to a real message.
- `voices.md` and SKILL.md now state the email form (answer-first quick replies, greeting and paragraph habits for longer emails, the constant sign-off) and the casual reply shape (the point, then one first-person line).
- `lint_andrew.py` thresholds were set against the samples. "Let me know if" is no longer reported in business email. One emphasis word per 150 words of business prose passes, and the generic per-word report is dropped inside that budget. "Actually", "basically", and "obviously" may each appear once in business prose. "Definitely" and agreement phrased as "agree 100%" are no longer treated as certainty claims in business prose; the natural register checks only "guaranteed", "100%", and "without a doubt". Sentence-initial "I" is judged as a share of at least six sentences. A long paragraph now means more than six sentences. Chat shorthand and "+" joins pass in the natural register. Two new items report a departure from his habits: two or more semicolons at a rate above one per 150 words, and, as a cadence note, a business email with no sign-off line.
- SKILL.md no longer routes to `research.md`, which is design provenance and not something a writing task loads. The README still points to it.

Evidence:

- `python -m unittest discover -s tests -v`: **75 tests passed**. The 68 from 4.4.0 are unchanged, and seven new tests in `tests/test_voice.py` cover the calibration with synthetic texts, each pairing a habit that must pass with a departure that must still be reported.
- `python scripts/validate_package.py --release`: passed. SKILL.md is 2,498 words against 2,500; SKILL.md plus its 11 routed references is 16,781 words against 18,000; the 62 eval cases have unique ids, and the 32 categorized cases cover the required categories with prohibitions.
- Run over the 80 sampled email bodies with the sign-off restored, the overlay's findings other than the straight-quote preference fell from 104 to 54, and emails with any such finding fell to 26. On the 40 `Custom` posts in the natural register, findings fell from 22 to 6.

What this does not show. Fewer findings on his own writing means the scanner contradicts the sample less. It is not a measure of voice fidelity, and no generated draft was compared with his writing by a reader. The eight new behavioral cases were not run against a model. The sample is one client project over two months plus replies on X, so essays, investor updates, cold outreach, and personal messages rest on the earlier guidance. The longer emails may have been drafted with assistance; the quick replies and the sentences he added to posts are the strongest evidence of his unedited phrasing. Twenty-four emails in the numbered range (037 to 048 and 061 to 072) were not supplied.

### Smoke run of the tuned skill

Two fresh model writers were each given only SKILL.md and the references it routes to, with the test cases, this file, and the tests withheld, and asked for eleven deliverables from invented briefs: quick replies, status and client emails, an admitted mistake, a scope boundary, casual replies, and a light proofread. The outputs were then read against the measured habits. This is one model, judged by the same session that tuned the skill; it is a check that the guidance produces the intended forms, not a blind comparison or a reader's verdict on likeness.

What held in every relevant output: the answer in the first words of a quick reply with no greeting; "Hi <name>," and status first in longer emails; paragraphs of about two sentences; the "Best regards," sign-off with the full name; first person and contractions; no semicolons, dashes, emoji, or hashtags; no invented facts; a quick-typed reply returned unchanged by the light proofread.

What the first run got wrong, and the fix: the scope email omitted his goodwill and the casual reply ended on a bare fact, because the 4.4 rule against sentiment the brief does not supply was suppressing his habitual warmth. `preservation.md` now separates that warmth, which is voice when the brief supports the act behind it, from invented apologies, promises, and feelings. In the second run the scope email led with wanting to keep the client and asked a clear either/or, and both casual replies ended on a first-person line.

What remains: the casual outputs are more restrained than his own posts, which use more emphasis and exclamation. A bare "Hi," appeared when no name was supplied, and an admitted mistake came without an apology; both are now covered in the profile and `preservation.md`, and those two edits were not re-run.
