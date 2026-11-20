# Decision report: building creator-intelligence

Prepared 2026-11-02. Manual review mode (research-first-creator): the local hunt accelerator was not configured and the awesome-repositories directory required sign-in, so discovery used GitHub search through `gh` only. No claim here was checked by an automated gate.

## What was asked

Combine two uploaded packs and expand them with research: the MIT-licensed ScrapeCreators social research skills, and the public `tigerless-labs/influencer-discovery` pipeline (GitHub lists no license for it). The result had to be a usable skill pack for HypeStake, a brand-creator deal platform.

## Candidates examined

Sixteen GitHub queries (literal terms, topic pairs, ecosystem terms, vetting terms) returned a small field. Fewer than five repositories were relevant, so all were examined and the rest were listed without inspection.

| Repository | Pinned commit | License (as read) | Inspected | Verdict |
|---|---|---|---|---|
| ScrapeCreators/social-media-research-skills | uploaded archive, upstream commit not recorded | MIT (LICENSE read) | all 13 skills and the validator | Adopted as the base, with live-verified corrections |
| tigerless-labs/influencer-discovery | uploaded archive, upstream commit not recorded | none (GitHub search listing: license none) | whole archive | Methods and measured findings only. No text or code is reused (see below) |
| kostja94/marketing-skills | 45143a7 | MIT | influencer-marketing skill | Rejected: a strategy outline with unsourced statistics such as "92% of consumers trust influencers" |
| NoxInfluencer/skills | 1547dc6 | MIT-0 | two SKILL.md files, directory listing | Idea only: an external benchmark must state source, date, market, population and metric definition. Adopted in the scoring rubric |
| mvanhorn/last30days-skill | 6894d44 | MIT | SKILL.md frontmatter and README mentions only | Referenced, not rebuilt: it already does cross-source topic research and uses the same ScrapeCreators key. Implementation not read |
| aaron-he-zhu/aaron-marketing-skills, unifapi-agent/agents, coreyhaines31/marketingskills | not pinned | Apache-2.0, MIT, MIT per search listing | not inspected | Listed only |

## Requirement to decision map

| Requirement | Adopted idea | Evidence | Implementation here |
|---|---|---|---|
| One entry from niche to shortlist | Stages with one owner each and a shared candidate record | Both packs; the pipeline's append-only log and dedup on (person, platform) | `skills/creator-research` router, record and status vocabulary |
| Find creators who bring an audience | Entry points per platform, directory versus search stop rules, niche signal from repeat authors | The pipeline's channel notes, restated as the plugin's own guidance with unmeasured yields removed | `skills/creator-discovery` |
| Capture the creator's own published contact | Two hops, attribution rules, hostile-page posture | Pipeline findings plus FTC and CAN-SPAM research | `skills/creator-contact-capture`, `scripts/contact_rules.py` (17 tests) |
| Do not recommend product founders as promoters | Content site versus product site gate | Pipeline finding, restated | `references/content-site-test.md` |
| Vet creators transparently | Gates plus weighted dimensions with confidence and bands | `research/03-vetting-methodology.md` | `skills/creator-vetting`, `scripts/creator_score.py` (13 tests) |
| Know what is lawful to scrape and email | Source policy table, pre-send gate, counsel questions | `research/02-legal-compliance.md` | `skills/outreach-compliance` |
| Correct data-layer facts | Endpoint, cost and quota corrections | `verification-2026-11-02.md`, 41 claims | `skills/scrapecreators-api`, `references/data-sources.md` |

## Decisions that depart from a source

1. **Deal inboxes are valid contacts.** The pipeline discards partnerships@, business@ and collabs@ addresses as role inboxes while also treating them as evidence of a seller. For a brand-deal platform the creator's own deal inbox is the intended contact, so `contact_rules.py` keeps it as `business_inbox` when it sits on the creator's own domain, and still rejects info@ and support@.
2. **Not AI-only.** The pipeline's topic gate has one hard-coded subject list. The plugin treats topic as a per-run input.
3. **No sending.** Both packs stop at contact capture. Compliance gates sit between this plugin and any sender.
4. **Third-party code is not vendored.** The pipeline carries no license, so default copyright applies. Its rules were restated in new structure and new wording, its code was not copied, and `PROVENANCE.md` records this. If you hold rights to it, say so and the code can be vendored.

## Not verified

- Whether the pipeline's own yield percentages hold. None is reproduced as fact.
- The pipeline's test suite was not run: executing code from the upload was blocked by the permission classifier.
- Live ScrapeCreators responses: no API key was used, so a 401 proves a route exists, not that it returns data.

## Unresolved

- Whether YouTube `paidProductPlacementDetails` is readable with an API key alone (docs silent).
- The GARM wind-down date: WFA's announcement is dated 9 August 2024, with 8 August quoted elsewhere. The plugin uses 9 August as the announcement date.
- Legal items labelled Reported in `02-legal-compliance.md` (ICO guidance, Texas and Vermont data-broker details, X and Reddit terms, status of X v. Bright Data).
- Whether Instagram business_email is always null in scraped responses (reported by the pipeline, not re-tested).

## Refuted

- "SociaVault is the only pay-as-you-go vendor with TikTok audience demographics." ScrapeCreators offers the same endpoint at the same cost, and other vendors expose audience data.
- "All transcript endpoints require video under 2 minutes." The 120-second cap applies to AI transcription and can be lifted; native captions have no fixed limit.
