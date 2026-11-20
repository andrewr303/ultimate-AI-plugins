# Citability and section rewrites

How to make a page's passages easier for AI answers to quote accurately without changing what the page says: the evidence behind passage-level work, the heuristic scorer, answer-first patterns, the rules for rewriting one section at a time, the deterministic fidelity gate, the change record, when evidence may be added, the citation-gap planner and the tactics that are off limits. This is the reference behind [geo-citability](../skills/geo-citability/SKILL.md).

As of 2026-11-01. Facts cite [current-facts.md](current-facts.md). Every threshold here is a house heuristic unless a fact ID is given.

## Evidence stance

- The GEO paper (KDD 2024) measured gains for sources that were already in a fixed retrieved context, with the largest gains for lower-ranked sources ([F-AI-31](current-facts.md#f-ai-31)). A replication benchmark (NeurIPS 2025 Datasets and Benchmarks) found most such rewriting methods largely ineffective, with gains shrinking as more sites adopt them ([F-AI-32](current-facts.md#f-ai-32)). Details and caveats: [geo-research-evidence.md](geo-research-evidence.md).
- Google says optimizing for generative AI search is still SEO and lists chunking content, rewriting for AI and special markup among misconceptions ([F-AI-12](current-facts.md#f-ai-12)).
- So treat citability work as editorial clarity that also helps human readers: direct answers, self-contained sentences, explicit subjects, real sources, clear structure. It is a readiness proxy (layer 2 in [measurement-protocol.md](measurement-protocol.md#four-layers)), never a citation promise.
- Access (crawlers allowed) and server rendering are preconditions. A page that AI crawlers cannot fetch or that renders its text only in the browser gains nothing from rewrites ([ai-crawlers.md](ai-crawlers.md), [seo-rendering](../skills/seo-rendering/SKILL.md)).

## Passage heuristics

`SG citability FILE --query "QUERY"` splits HTML or Markdown into passages at headings and scores each one from 0 to 100 in five parts. The score is a transparent heuristic (evidence class C, English-only patterns), not a prediction of citation.

| Part | Cap | What earns points (approximately) |
| --- | --- | --- |
| Answer | 30 | A definition pattern ("X is a ..."), an answer in the opening words, a question heading, sentences of readable length, an attribution phrase |
| Self-contained | 25 | A passage length inside the house band, few dangling pronouns, named entities instead of "it" or "this" |
| Structure | 20 | Moderate sentence length, ordering words, numbered steps, line breaks |
| Statistics | 15 | Percentages, amounts, numbers with units, years near the current date, named sources |
| Uniqueness | 10 | First-party research or experience markers, concrete examples, named tools |

| Grade | Score |
| --- | --- |
| A | 80 and above |
| B | 65 to 79 |
| C | 50 to 64 |
| D | 35 to 49 |
| F | below 35 |

Aggregates: `mean_all` (every passage), `mean_top5` (the five best passages; useful for long pages where navigation text drags the mean down) and `coverage_70` (share of passages scoring 70 or more). Report all three and label them heuristic.

House heuristics, labelled every time they are used:

- A self-contained passage of about 134 to 167 words scores best; 100 to 200 words is acceptable. The origin of the 134-167 figure is an unverified third-party analysis; we keep it only as a band.
- A direct answer within the first 40 to 60 words of a section.
- Passages between 40 and 300 words for [CITE003](rule-catalog.md#cite003).

How to read the score:

- The statistics and attribution parts reward numbers and phrases such as "according to". Never add a number, a source name or "according to" to raise the score; add evidence only under the policy below.
- A low score on a navigation block, legal text or a code sample is normal. Choose target sections that answer real queries.
- Compare scores for the same page before and after one change, with the same query. Do not compare across sites.

Related lint: `SG content-lint FILE` reports quantitative or authority claims without a nearby citation ([CONT001](rule-catalog.md#cont001)), paragraphs that open with dangling references ([CONT007](rule-catalog.md#cont007)), hype ([CONT008](rule-catalog.md#cont008)), orphan citation markers ([CONT009](rule-catalog.md#cont009)) and leftover AI or template artifacts ([CONT004](rule-catalog.md#cont004)). Low passage scores are [CITE001](rule-catalog.md#cite001); question headings not answered early are [CITE002](rule-catalog.md#cite002).

## Answer-first patterns

Use facts already on the page. These are editorial patterns, not formats any engine requires ([ai-surfaces.md](ai-surfaces.md#reader-first-structures-by-query-type)).

| Pattern | Shape | Before (synthetic) | After (same facts) |
| --- | --- | --- | --- |
| Definition | "[Subject] is a [category] that [function]." | "When people talk about pro forma invoices, they usually mean a preliminary bill. It is sent before work starts or goods ship, so the buyer can approve the cost." | "A pro forma invoice is a preliminary bill sent before work starts or goods ship, so the buyer can approve the cost." |
| Direct answer then detail | First sentence answers; the rest explains | "There are many factors to consider. In most cases, account approval takes 2 business days." | "Account approval usually takes 2 business days. The time depends on ..." |
| Named subject | Replace "it", "this", "they" with the noun | "It supports CSV export." | "The invoice dashboard supports CSV export." |
| Scoped claim | Conditions stated with the claim | "Payments arrive in 3 days." | "Card payments arrive in 3 business days in the US; other methods vary." (only if the page already states both parts) |
| Steps | Numbered list for an existing sequence | A paragraph listing actions with "then" | The same actions as an ordered list |
| Comparison | Table with the same criteria for each option | Two paragraphs describing options differently | One table, units explicit, unknowns shown as "not stated" |

Bad patterns: chopping a page into tiny fragments for machines, synonym stuffing, repeating the query in every sentence, and question headings that the section does not answer.

## Section-rewrite rules

Rewrite one section at a time, for one real query. Adapted from the eGEOagents section-rewriter rules (MIT), whose hard rules map one-to-one onto the fidelity gate.

Hard rules (breaking any makes the rewrite unusable):

1. Keep the heading line exactly as it is.
2. Keep every link, URL, number, date, percentage, price, version and name. Add none.
3. Keep every table row and every code block exactly as they are; text may be added around them, never inside.
4. Add no facts, statistics, claims, promises, comparisons or superlatives ("best", "leading", "ultimate", "revolutionary", "comprehensive") that the section does not already support.
5. Keep caveats, limitations and honest qualifiers ("not a guarantee", "one snapshot", "a proxy", "may", "in our tests").
6. Keep the length between 80% and 160% of the original (heuristic, applied when the original has at least 20 words).
7. Keep the language, voice and tone; keep the page's spelling conventions.

What the rewrite may do:

- Put a direct, self-contained answer to the query in the first sentence after the heading, using facts already in the section.
- Use the query's own wording where it is accurate.
- Reorder sentences so the most relevant facts come first.
- Split long paragraphs, or turn an existing enumeration into a list.
- Name the subject explicitly instead of "it" or "this" so a quoted sentence stands on its own.

Never paste competitor text, or text from pages that currently get cited, into the rewrite. Read them, if at all, only to understand what question they answer.

Whole-page rewrites are discouraged: in eGEOagents' own published runs (2026-10-04, gpt-4o), long well-sourced pages lost about a third of their words, including the "last verified" date, primary-source links and specific data points, while the tool's keyword score rose (project self-report, https://github.com/mverab/eGEOagents, `docs/examples.md`). Section-level edits with a deterministic gate exist to prevent exactly that.

Workflow with the CLI (the CLI never edits files in place):

```bash
SG sections list content/guide.md
SG sections show content/guide.md --id s03 --output .seo-geo-god/work/guide-s03.original.md
# write the rewrite of that section to .seo-geo-god/work/guide-s03.rewrite.md
SG fidelity .seo-geo-god/work/guide-s03.original.md .seo-geo-god/work/guide-s03.rewrite.md
SG sections replace content/guide.md --id s03 --with .seo-geo-god/work/guide-s03.rewrite.md --diff
```

Apply the reviewed diff with the editor tool. Section IDs (`s00` for any preamble, then `s01`, `s02` in order) come from ATX headings outside fenced code; frontmatter and every other byte stay unchanged.

## Fidelity gate

`SG fidelity ORIGINAL REWRITE` compares two Markdown or HTML fragments and exits 1 when any check fails. Thresholds come from `data/thresholds.json` (`min_ratio` 0.8, `max_ratio` 1.6, `min_words` 20; heuristic) and can be tightened with `--min-ratio` and `--max-ratio`.

| Rule | Violation | What it catches |
| --- | --- | --- |
| [FID001](rule-catalog.md#fid001) | `heading_changed` | The first heading line differs |
| [FID002](rule-catalog.md#fid002) | `link_removed:<url>` | A link or URL disappeared (Markdown, autolinks, bare URLs, HTML anchors, reference definitions) |
| [FID003](rule-catalog.md#fid003) | `link_added:<url>` | A new link appeared |
| [FID004](rule-catalog.md#fid004) | `number_removed:<n>` | A number, price or percentage disappeared (numbers inside URLs and code are ignored) |
| [FID005](rule-catalog.md#fid005) | `number_added:<n>` | A new number appeared |
| [FID006](rule-catalog.md#fid006) | `table_rows_decreased` | Fewer table rows |
| [FID007](rule-catalog.md#fid007) | `code_block_changed` | Any fenced code block changed |
| [FID008](rule-catalog.md#fid008) | `too_short` or `too_long` | Word ratio outside the allowed range |
| [FID009](rule-catalog.md#fid009) | `superlative_added:<word>` | A superlative the original did not use |
| [FID010](rule-catalog.md#fid010) | `caveat_removed:<phrase>` | A hedge or limitation phrase disappeared |

Limits of the gate: it does not catch numbers written as words, reordered table rows, changed meaning with the same numbers, or a dropped claim that had no number or link. After the gate passes, re-read both versions and answer one question for the rewrite: does it keep every fact, number, link and caveat of the original and add no new claim? Classify it as faithful, drops facts or adds claims. This self-check can only reject a rewrite; it never overrides a failed gate. A failed gate means the rewrite is redone or dropped, never "accepted with exceptions".

## Change record

Every applied rewrite gets a [change record](../templates/change-record.md): element, before, after, why, evidence; the `[needs source]` list; the fidelity result; and the re-measure list. Keep the states distinct: prepared, implemented locally, deployed, measured.

## Evidence additions policy

Statistics and quotations helped in the GEO paper's lab setting ([F-AI-31](current-facts.md#f-ai-31)), which is exactly why they are the most tempting thing to fabricate. Add evidence only when:

- the user supplies the data (internal analytics, survey results, product facts) and confirms it may be published; or
- a verifiable primary source is found, read and linked, with its date, denominator and method stated next to the number; or
- a real, named person gave a quotation the owner can attribute and has permission to publish.

Otherwise leave a `[needs source]` note in the draft notes or the change record, never in published text, and never replace it with an invented number, quote, author, review or date. When a supporting number does not exist, rewrite the claim to what is known, or drop it. Evidence additions are separate changes from structural rewrites and go through the fidelity gate as `number_added` or `link_added` that the reviewer accepts explicitly.

## Citation-gap planner

`SG gaps plan TRACKER --project .seo-geo-god/project.json` turns an AI-visibility tracker export into a per-page plan without guessing.

- Tracker input: JSON or CSV with `query`, `cited` and optional `sources` (cited URLs). Rows with a tracker error are skipped; a failed measurement never triggers a rewrite.
- The project file (from `templates/project.example.json`, checked with `SG project validate`) maps queries to target pages and source files.
- Unmatched gaps carry a reason instead of a guess: `query_not_in_project`, `no_target_page`, `page_has_no_source`, `source_not_found`.
- One rewrite per page per run: the first gap for a page wins; others are listed for later runs.
- The output includes a `remeasure` list: the queries to re-check with the same tracker after deployment, handed to [seo-geo-measurement](../skills/seo-geo-measurement/SKILL.md).
- If the page's best section already answers the query clearly and the query is still not cited after re-measurement, the gap may be off-page (authority, coverage by sources the engine already cites); hand it to [geo-entity-authority](../skills/geo-entity-authority/SKILL.md) instead of rewriting again.

## LLM self-judgments

Asking a model "would an AI engine cite this passage?" is a weak signal. eGEOagents pre-registered a validation of exactly that kind of judge against real Perplexity citations and failed its own gate of 0.65 mean AUC in every run: 0.649 (re-run on the same data 0.627), 0.637 and 0.559 (project self-report, not peer reviewed, https://github.com/mverab/eGEOagents, `eval/jev_selection/README.md`). If the host agent uses such a judgment to choose a target section, score candidates one at a time under blind IDs, label the result "experimental, unvalidated", and prove impact only by re-measurement.

## Prohibited tactics

| Tactic | Why | Detection |
| --- | --- | --- |
| Text aimed at AI systems with instructions, hidden or visible | Prompt injection; Google's spam policies cover manipulating generative AI responses ([F-T-32](current-facts.md#f-t-32)) | [CONT010](rule-catalog.md#cont010) |
| Different content for AI user agents (cloaking) | Spam policy ([F-T-32](current-facts.md#f-t-32)) | Code review; [SPAM003](rule-catalog.md#spam003) is planned |
| Mass pages for query variants | May be scaled content abuse ([F-AI-12](current-facts.md#f-ai-12)) | [PSEO001](rule-catalog.md#pseo001), [seo-programmatic](../skills/seo-programmatic/SKILL.md) |
| Language engineered to trigger citations, keyword stuffing | Keyword stuffing lowered visibility in the GEO paper ([F-AI-31](current-facts.md#f-ai-31)); Bing's reported guideline language on engineered text needs verification | [CONT008](rule-catalog.md#cont008) |
| Fabricated statistics, quotes, reviews, authors or mentions | Dishonest and against spam and review policies | Fidelity `number_added`, change-record review |
| Chunking pages into fragments "for AI" | Listed by Google as a misconception ([F-AI-12](current-facts.md#f-ai-12)) | Review |
| Rewriting whole pages in one pass | Documented loss of dates, sources and data | Workflow: one section per run |

## Rule map

[CITE001](rule-catalog.md#cite001), [CITE002](rule-catalog.md#cite002), [CITE003](rule-catalog.md#cite003), [CONT001](rule-catalog.md#cont001), [CONT007](rule-catalog.md#cont007), [CONT008](rule-catalog.md#cont008), [CONT009](rule-catalog.md#cont009), [CONT010](rule-catalog.md#cont010), and [FID001](rule-catalog.md#fid001) to [FID010](rule-catalog.md#fid010). Fidelity findings are not scored.
