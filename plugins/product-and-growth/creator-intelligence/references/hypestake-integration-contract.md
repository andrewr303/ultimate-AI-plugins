# HypeStake re-integration contract

This plugin is meant to move back into HypeStake's AI features. This file says how its records, rules and skills map onto what the platform already has, where they conflict, and what a platform caller must keep. Provider facts and the discrepancy table are in [hypestake-platform-map.md](hypestake-platform-map.md).

Status: a **proposal**. Nothing here is wired into HypeStake. Checked against HypeStake source `77a68e5c` and the STAR project (`projects/hypestake-star/`) on 2026-11-10, read only. Every type and field name below was found by search in those trees; paths are relative to the HypeStake root, with `star:` for the STAR project. HypeStake vendors the STAR Finder kernel at `src/shared/star/finder/`. A recursive diff of `star:src/finder/` against it on 2026-11-10 found every file byte-identical except two: `contact.ts` (the STAR package has the email-boundary fix and the linear `scanEmails`, port version `hs-finder-ts-1.0.1`) and `version.ts` (STAR says `hs-finder-ts-1.0.1`, HypeStake still `hs-finder-ts-1.0.0`). HypeStake gets the fix only when it re-vendors with `star:scripts/vendor-to-hypestake.mjs`. Rows below that describe STAR contact behaviour describe the STAR package.

## 1. What to vendor

| Plugin piece | Vendor into HypeStake? | How |
|---|---|---|
| `src/contact-rules.ts`, `src/creator-score.ts` | Yes, as advisory kernels | Pure, ES2020 library, relative `.ts` imports, no Node built-ins, no regex lookbehind. Same shape as `src/shared/star/`. Copy with `vectors/*.json` and `test/vectors.test.ts`, run under the Vitest node project |
| `scripts/*.py` | No | Python reference for the skills and the vectors. Keep it here, as HypeStake keeps the Python mirror of the Genome kernel in `services/genome_metrics/` checked against golden fixtures |
| Skills | As playbooks, not code | Into `ai-knowledge/third-party/` or `src/lib/star-agent/skills/definitions/`, after the vocabulary in the platform map |

The kernels' wire shape is snake_case JSON, identical to the Python command line, so one contract serves skills, kernels and vectors. An adapter in `src/shared/star-adapters/` should translate to camelCase platform types, as the existing Finder adapter does.

## 2. Candidate record to STAR Finder kernel input

Plugin record: `skills/creator-research/SKILL.md`, "The record every stage passes on". Kernel input: `CandidateEvidence` and `CandidateContext` in `star:src/finder/candidate.ts`; platform adapter type `FinderCandidate` in `src/shared/star-adapters/finder/candidates.ts`.

| Plugin field | Kernel field | Mapping |
|---|---|---|
| `platform`, `handle` | none in `CandidateEvidence` | `candidateRef` must be opaque (`creator-<uuid>` or a registry id), never a handle, name, URL or hash of one. The adapter mints it and keeps the handle elsewhere |
| `audience.value`, `audience.unit`, `audience.as_of` | `audience: Known<{ value, unit, ageDays }>` | Transform. `ageDays` = days from `as_of` to the adapter's `now`. `unit: "none"` or a null value becomes `{ state: "unknown", reason }`, never 0. Plugin units `views` and `plays` are not in STAR `AudienceUnit` and have no `ADMISSION_PARAMS.minAudience` row, so they cannot admit a candidate |
| `own_site` | `platformLinks: string[]`, `ownership` | Transform and gap. The plugin keeps only the declared own-site link; the kernel wants every profile link so `classifyLink` can sort aggregators, payment and platform domains. Ownership (`rel=me`, author schema, name or handle in the domain) is not collected by the plugin |
| bio addresses kept with page `bio` | `platformBioEmails` | 1:1 as raw strings, but see conflict C14: raw addresses go only to a vault writer |
| pages fetched in contact capture | `pages: FetchedPage[]` | Transform. Page kinds: `bio` to `platform_bio`, `homepage`, `contact`, `about`, `sponsor`, `legal` 1:1. Plugin `roster` and `footer` have no `PageKind`; STAR `aggregator` and `media_kit` have no plugin label. Status: `robots_decision: disallowed` to `robots_disallowed`, a 403 to `http_403`, click-to-reveal to `click_to_reveal`. Gap: the plugin keeps contacts, not page text, so the run must hand page text to the kernel before discarding it |
| `signals` (`product_pusher`, `sells_own_product`) and the content-site tally (`references/content-site-test.md`) | `ownerEvidence: OwnerEvidence` | Transform. Feed link to `structural.feed`; newsletter or podcast host to `newsletterPlatform` or `podcastFeed`; sponsor or media-kit page to `sponsorEvidence[]` with `confirmedByContextFetch`; checkout script to `checkoutScript`; plan pricing to `perSeatPricing`; keyword hits to `keywordHits` (recorded, never scored, in both) |
| vetting posts (`outlier_report` input) | `posts: Post[]`, `postDaysAgo: Known<number[]>` | Transform. `age_hours / 24` to `daysAgo`; caption text to `text`; a paid-partnership flag to `paidPartnershipLabel`. A post with unknown age is left out of `postDaysAgo` |
| `country` | `Account.country` (`star:src/finder/identity.ts`), scope checks | 1:1 when declared; null stays null |
| `/v1/find-social-profiles` matches | `Account[]` for `resolveIdentity` | Transform: `accountKey`, `platform`, `canonicalUrl`, `handle` with `handleSource: "platform"`, `linksTo`. The provider's `confidence` is not a Fellegi-Sunter weight: keep it as a lead, not a `link` anchor |
| G4 (identity unverifiable) | `identity: "resolved" \| "ambiguous"` | A G4 record is `ambiguous`. A record without G4 is not automatically `resolved`: that needs `resolveIdentity` |
| G1 (brand-safety floor) | `SafetyScreen` from `screenSafety` | Different rules. The kernel fails only on a platform label or measured text and holds a model label. Do not pass G1 as a kernel fail |
| G3 (insufficient data) | unknown states with reasons | Do not translate to a fail |
| G2 (inauthentic audience), G5 (undisclosed sponsorship) | none | No kernel gate. Keep as advisory evidence |
| `contact_tier` | `contactPath: ContactPathState`, `platformMessaging` | `email` or `business_inbox` to `business_contact_found`; `dm_only` to `platformMessaging: true`; `none` after every planned page to `none_found`; obfuscated or blocked to `obfuscated_respected` or `stopped_at_boundary`. Gaps: `form` and `manager_listing` have no kernel state |
| `status` | `Outcome` (`OUTCOMES` in `star:src/finder/qualification.ts`) | No 1:1 mapping. Plugin statuses are research statuses. Never set a Finder outcome from them; let `evaluateCandidate` decide |
| `score`, `band`, `confidence`, `dimensions` | none | The kernel has no creator score. Do not feed it into `FinderMatch` (that is the Match Score v2 term) |
| `query`, `seen_count`, `logged_at`, `reason` | none | Run ledger and provenance only |

**Kernel inputs the plugin does not collect:** `homeBase`, `isStaffAuthor`, `rhythmSustained` (the plugin's discovery test has "repeat output" but records no boolean), `optedOut`, `accountState`, `exclusivity`, `modelFlags`, `publicText`, `bm25`, `modelOnTopic`, `scope`, `preferences`, `matchGated`.

**Gaps INTEGRATION.md names that this plugin fills.** `docs/product/specs/star/INTEGRATION.md` says the Finder kernel lacks "post records, platform links and owner evidence" that HypeStake does not collect today. The plugin collects all three from public data: post records with age and metric in vetting (`outlier-post-finder`, `creator-vetting` step 3), declared links in discovery and contact capture, and owner evidence through the content-site test. It also collects the contact path the Finder adapter leaves unknown ("contact capture is off, decision D5"), which must stay off in HypeStake until D5 changes (C14).

## 3. Candidate record to the Creator Finder v2 contract

Contract: `src/shared/creator-finder/finderV2.ts` and `finder-v2.schema.json`; criteria panel: `design_handoff_discover_creators_agent/CRITERIA_CONTRACT.md`.

| Plugin field | Finder v2 field | Mapping |
|---|---|---|
| `platform`, `handle` | `FinderCandidateIdentity { platform, handle }` | 1:1 (handle without `@`, at most 256 characters). `FinderDiscoveryPlatform` lists only instagram, tiktok, youtube, twitch, twitter, facebook, spotify, soundcloud: plugin records on threads, bluesky, mastodon, reddit, podcasts or newsletters cannot be a discovery proposal |
| `sources[]` (new provenance field, section 6) | `FinderEvidence` | Transform: `provider`, `source_ref` (the endpoint or page kind), `url`, `fetched_at` = `collected_at`, `observed_at` = `as_of` (null when unknown), `source_kind` = `public_web` for pages, `platform_api` for an official API. A ScrapeCreators row is a provider row; HypeStake already has a convention for ScrapeCreators rows (`src/lib/runtime/creator-finder/agentCoreDiscovery.ts`): `source_kind: "platform_api"`, `source_id: "scrapecreators"`, `provider: "scrapecreators"`, and `source_ref` as `scrapecreators:` plus the endpoint path, for example `scrapecreators:/v1/tiktok/profile`, with `#follower_count` for a follower count and `#post` for a post record (`scrapecreators:/v3/tiktok/profile/videos#post`). Its Google search lane is `source_kind: "public_web"`, `source_id: "scrapecreators_google"`, `provider: "scrapecreators"`. Use the same values |
| audience | `FinderFieldObservation` | Known: `value`, `unit`, `provider`, `source_id`, `evidence_ids`, `confidence`. Unknown: `value: null`, `confidence: "unavailable"`, `missingness_reason` (for example `search_count_zero_filled`) |
| three-part candidate test (`creator-discovery` step 3) | `FinderResearchQualification` | `entity_kind`: a person is `individual`, a show or newsletter run by several people is `collective`; `entity_evidence_urls` from the profile and own site; `relevance_evidence[]` `{ reason, url, excerpt }` from the niche posts that passed "repeat output" |
| creator type | `FinderDiscoveryProposal.creator_type` | The plugin does not record one. Leave unset rather than guess |
| creator score | `FinderDiscoveryProposal.fit_score` | **Do not map without a product decision.** `fit_score` is the agent's own ordering estimate; the creator score is a different, gated summary. Mapping it would turn a research summary into a ranking input |
| `country` | `criteria.location` (strict scope) | Declared country only. CRITERIA_CONTRACT says a strict filter with an unknown field excludes an external candidate; a null `country` must not be filled by guess |
| `contacts[]` | none | The contract has no contact field, by design |

## 4. Contact rules: plugin versus STAR `contact.ts` and `owner.ts`

Plugin: `scripts/contact_rules.py` and `src/contact-rules.ts`. STAR: `extractBusinessContacts` and `planContactHops` in `star:src/finder/contact.ts`; `classifyAudienceOwner` and `bringsOwnAudience` in `star:src/finder/owner.ts`. The column "Authoritative for HypeStake" is a recommendation for the platform owner, with the reason; it is not applied anywhere.

| # | Difference | Plugin | STAR kernel | Authoritative for HypeStake |
|---|---|---|---|---|
| C1 | `hello`, `hi`, `contact`, `info`, `team`, `press`, `media`, `inquiries`, `enquiries` on the own domain | `reject_role` | kept as `own_domain_business_inbox` (`BUSINESS_LOCALS`) | **Decision needed.** STAR keeps more real inboxes; the plugin refuses inboxes that serve customers. Recommend STAR for a deal-sending platform, because the own-domain check limits the risk, but it is a product call |
| C2 | Deal-style local on a free-mail domain (`business@gmail.com`) | `reject_role` | `free_mail_listed`, kept, unless an earlier check drops it: malformed, asset filename, unknown TLD, `PLACEHOLDER_LOCALS` or placeholder domain, `LEGAL_LOCALS`, `COMPANY_FUNCTION_LOCALS` all run before the free-mail branch. A deal-style local such as `business` passes those, so it is kept | STAR, once D5 allows storage: a creator who publishes `business@gmail.com` chose it. Until then neither is stored |
| C3 | Personal-looking address on a third-party domain | `personal`, kept | `third_party_domain`, kept with `needsReview: true` | STAR: the review flag is the safer default |
| C4 | Own domain | trusts the caller's `site_domain` | only domains `classifyLink` verifies as `own_site` (rel=me, author schema, name or handle in the domain) | **STAR.** The plugin's guard depends on the caller |
| C5 | Address on 3 or more fetched pages | `reject_footer` | kept; `extractBusinessContacts` counts the pages an address appears on (`pages`) and keeps the highest-priority page kind. It has no footer rule and does not subtract template domains during extraction (`templateDomains` is used only by `classifyLink`, `classifyAudienceOwner` and `evaluateCandidate`, to decide own sites and sponsor evidence) | Decision needed. The plugin's rule loses a real contact the creator repeats in a footer; STAR's keeps a site-wide or template address. Neither is clearly right |
| C6 | Placeholder locals `me`, `your`, `example`, `test` | not placeholders (`me@` is `personal`) | `PLACEHOLDER` | STAR: stricter, no loss of a real contact likely |
| C7 | Function inboxes `orders`, `returns`, `notifications`, `mailer-daemon` | `personal` (not in any list) | `COMPANY_FUNCTION_INBOX`, dropped | **STAR.** This is a gap in the plugin's lists, recorded and not patched here to keep the vectors stable; add it in both implementations when the lists are next reviewed |
| C8 | `trust@` | `reject_legal` | not listed | Plugin, low impact |
| C9 | TLD check | syntax only, 2 to 24 letters | against a caller-supplied IANA set (`tlds`) | **STAR** |
| C10 | Domain end in text extraction | refuses a match followed by a letter, digit, `_`, `-`, a non-ASCII character, or a `.` plus a letter or digit (0.2.0) | the STAR package has the same lookahead, `(?![A-Za-z0-9_-]\|\.[A-Za-z0-9]\|[^\x00-\x7F])` (`hs-finder-ts-1.0.1`); HypeStake's vendored `src/shared/star/finder/contact.ts` still has the open-ended pattern, so `jane@janedoe.com2` yields `jane@janedoe.com` there | Agree now. HypeStake must re-vendor with `vendor-to-hypestake.mjs` to get it |
| C11 | Decoding | `\uXXXX` (not surrogates), `\n \r \t`, numeric entities, eight named entities | `&#d;`, `&#x;`, `&commat;`, `&period;`, `&amp;`, `@`, `\n \r \t` | Equivalent for addresses. Either |
| C12 | Fetch scope | homepage, one contact or about page, one sponsor page | aggregator once, homepage, then up to `maxSubpages` 4 of sponsor, media kit, contact, about; 3 seconds between requests | **STAR** for HypeStake (its egress point enforces it); the plugin's policy table is narrower and should stay so for standalone use |
| C13 | Obfuscated or click-to-reveal address | stop, record nothing, `no_contact` | `obfuscated_respected`, which counts as a contact path in `reachability` | Both refuse to decode. STAR is authoritative for reachability: a hidden address still shows a contact surface |
| C14 | Storing raw addresses | `contacts[].value` goes to the user's own sheet or database | returned only as `contactsForVaultWriterOnly`; everything else carries `contactSummary` counts and opaque refs; contact capture off until decision D5 | **STAR and D5.** In HypeStake no address is stored, logged or traced until D5 is decided |
| C15 | Product site | product signals only: `buyer`, no contacts | `product_founder` rejected only with no audience evidence and at least two independent product signals; otherwise review (decision D1, `review_with_audience`) | **STAR (D1 is applied).** The plugin's `buyer` should map to review unless the two-signal, no-audience test holds |
| C16 | Sponsor evidence | a sponsor page or deal inbox nominates; keywords never count | the same, plus confirmation by a second context fetch on a verified own domain | STAR |
| C18 | Start and length of a match in text extraction | the candidate must start with a letter or digit, must not follow a local-part character or any non-ASCII character, and is bounded: local part 64, labels 63, domain 253, top-level label 2 to 24 letters | `scanEmails` takes the longest run of `[A-Za-z0-9._%+-]` before "@" (it may start with `.`, `%`, `+` or `-`), a domain of `[A-Za-z0-9.-]` (empty labels allowed), a top-level label of 2 or more letters; it then drops a local part over 64 characters in its address check, and bounds no label or domain length | Decision needed, low impact. Both run in linear time. Measured on 2026-11-10: `x.jane@janedoe.com` gives the whole address in both; `-jane@janedoe.com` gives `-jane@janedoe.com` in STAR and nothing in the plugin; a 65-character local part gives nothing in both. The plugin is stricter (fail-closed) on starts, labels and domain length |
| C17 | Refused routes | WHOIS, GitHub profiles, `/humans.txt`, `security.txt`, OCR, guessing | `REFUSED_CONTACT_ROUTES`: `rdap_whois`, `commit_metadata`, `security_txt`, `image_ocr`, `guessed_address` | Agree. Add `humans_txt` to the platform list if wanted |

## 5. Per-skill platform surface and tool contract (proposal)

HypeStake requires every tool to state input and output schemas, side effects, permission tier, timeout, retry, idempotency key and audit fields, and to default-deny (`CLAUDE.md` section 6). Proposed contracts:

| Skill | HypeStake surface | Input sketch | Output sketch | Side effects | Permission tier | Timeout | Retry | Idempotency key | Audit fields |
|---|---|---|---|---|---|---|---|---|---|
| `creator-research` | STAR Scout skill in the Assistant (Render Studio chat); run report for Discover creators | brief: `target_count`, admitted criteria, priorities | run report: decisions, per-channel counts and stop reasons, status distribution | none | read-only | n/a (orchestrates) | n/a | `search_id` | `search_id`, skill version, stages run |
| `creator-discovery` | Creator Finder internet arm (`source_creator_candidates_v2`), Render `platform_runtime` | `{ topics, platforms, followers, location }` public terms only, `permitted_sources`, budget | `FinderCandidateProposal[]` plus `FinderEvidence[]`, `FinderReceipt[]` | paid provider calls, through the run's credit reservation | Brand-scoped, server-side | per call 20 to 25 s, bounded by the run deadline | no re-send of a paid call after an uncertain outcome; next run may retry | `(search_id, stage_id, attempt.fence)` | provider, endpoint, credits charged, cached, `cached_at`, receipt status |
| `creator-contact-capture` | Finder contact hop (`planContactHops`, `extractBusinessContacts`), **off until D5** | candidate ref, verified own domains, fetched pages | `contactSummary` (state, kinds, counts, opaque refs); raw addresses to a vault writer only | page fetches through the read-only egress point; vault write after D5 | service path, never a browser client | 3 s between requests per host; stop on 403, 429, CAPTCHA, login | none after a block | `(candidate_ref, page url)` | robots decision, status code, timestamp per fetch; dropped counts |
| `creator-vetting` | STAR Scout vetting in the Assistant; advisory evidence next to Discover results | posts, dimensions with evidence, gate codes, brand safety configuration | `outlierReport` and `scoreCreator` output | none (pure); paid post pulls are separate tool calls | read-only | kernel: synchronous | n/a | input hash | `CREATOR_SCORE_VERSION`, `rubric_version`, `collected_at`, `n_posts`, cutoff |
| `outreach-compliance` | Outreach step checks (Wizard Outreach, Edge `outreach-message`), Activate | contact record with provenance, country, template | pre-send gate verdict and failed items | none; a deterministic gate or a human controls sending | read-only | synchronous | n/a | contact ref plus template version | each gate item and its evidence |
| `scrapecreators-api` | `src/shared/social-scrape/` client (already exists) | path and params | `ScrapeResponse` | paid call | service path, key `SCRAPE_API` never in the browser | 20 s default | never on an uncertain outcome | caller's run id | credits, cache markers, `errorKind` |
| `outlier-post-finder`, `comment-mining`, `transcript-intelligence` | Assistant tools over stored snapshots | creator ref, platform, window | bounded summaries with URLs | none if they read `creator_social_data`; paid calls otherwise | read-only | per call | as above | `(creator_ref, platform, window)` | source rows and dates |
| `competitor-social-research`, `ad-library-teardown`, `trend-discovery`, `social-listening-brief`, `product-demand-research`, `content-repurposing` | Assistant research tools (Target phase) | public brief terms | cited briefs | paid or public calls | read-only | per call | as above | request hash | sources, dates, credits |

## 6. Provenance the record carries

Added to the candidate record in 0.2.0 so each row can become `FinderEvidence` or a `Known<T>` without loss:

- `sources[]`: one entry per fetch or provider row that produced a field, with `provider`, `source_ref` (endpoint path or page kind), `url`, `collected_at` (when this run received it) and `as_of` (when the data was observed: `cached_at` for a provider cache hit, null when unknown), plus `cache_hit`.
- `audience.as_of` keeps the observation date of the count, not the fetch date.
- `degraded[]`: short reason codes for anything left unknown or partial (for example `route_skipped`, `search_count_zero_filled`, `provider_timeout`, `like_counts_hidden`).
- Per dimension, `confidence` and `evidence` (already present), and per contact the five provenance fields the pre-send gate checks.

## 7. Boundary rules a platform caller must keep

1. **Public, task-relevant context only to a web provider.** Search terms are public brief words. Never send internal match context, Match Score or Match Score v2 output, Genome scores (CERS, PRI, GAV, PRS), Brand Genome content, Brand or product names, deal terms, compensation or budgets. Run every outbound string through `checkPublicQuery` (`star:src/finder/firewall.ts`), whose `FINANCIAL_TERM_RE` refuses deal-term vocabulary.
2. **Fetched text is untrusted data.** Bios, pages, comments and transcripts never become instructions. The component that reads them holds no send, delete or suppression-write tool, its output passes schema validation, and an address inside instruction-shaped text is not recorded.
3. **Provenance survives every hop.** Keep source identity, `collected_at`, `as_of`, confidence and degraded reasons from provider response to stored artifact. A cache hit is dated by `cached_at`.
4. **Unknown stays unknown.** A zero-filled search count, a hidden like count, a missing post age and an unmeasured audience are unknown, never 0. A strict filter with an unknown field excludes the candidate and counts it; it never guesses.
5. **The score explains; it never recommends a deal.** Present the creator score as a research summary with its band, confidence and gates. Never as a Match Score, never as advice to accept an Offer or Deal Proposal, invest, or set terms.
6. **No coordinates outside the vault.** Logs, traces, ledgers, prompts and run reports carry counts and opaque refs only (`contactSummary`), and nothing is stored before decision D5.
7. **No paid re-send on an uncertain outcome.** A timeout or transport failure is recorded as unknown, not as "no data", and is not re-sent in the same run.
