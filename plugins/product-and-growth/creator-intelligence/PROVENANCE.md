# Provenance

Creator Intelligence combines two uploaded packs and adds research. This file says what came from where, what was checked, and what was not.

## Sources

| Source | License | What was used | How |
|---|---|---|---|
| ScrapeCreators/social-media-research-skills | MIT, notice kept in `LICENSE` and `NOTICE` | Thirteen skills as the base of the plugin | Copied, then corrected against the live API spec, and three skills merged into the new discovery and vetting skills |
| tigerless-labs/influencer-discovery | None. GitHub lists license "none", and the uploaded archive has no license file | Ideas, rules and measured findings about discovery, contact capture and the content-site versus product-site test | Restated in new structure and wording. The working tree reproduces no yield percentages as fact. A review after the rewrite still found passages that follow its phrasing in places, and those were reworked again. Treat the restatement as derived from an unlicensed source until the owner's decision below is made |
| kostja94/marketing-skills, NoxInfluencer/skills, mvanhorn/last30days-skill | MIT, MIT-0, MIT | Read for comparison at pinned commits | One idea adopted (state source, date and definition for any external benchmark). Nothing copied |
| Primary sources listed in `research/` | Not applicable | API specs, statutes, regulator pages, standards | Cited with URLs and labelled Confirmed, Reported or Unverified |

## Process

1. Both archives were unpacked into an isolated directory and read in full. Embedded code was not executed.
2. Three research agents checked API and vendor facts, legal and platform constraints, and vetting methodology (`research/01` to `03`).
3. Three adversarial verifiers re-checked the highest-impact claims against primary pages (`research/verification-2026-11-02.md`, `research/ledger/`).
4. Four authors wrote the new skills with disjoint file ownership, four reviewers audited them, and a second fix pass resolved their findings, including three provenance blockers that led to the rewrite of the contact rules and the two contact-capture references.
5. A three-lens recheck ran after the fixes. It confirmed 39 passing tests and resolving links, and still found provenance and consistency issues, which a third pass addressed (rename of the content-site note, reworked passages, alphabetised word lists, label and cross-reference fixes). No fourth full review was run, so the provenance judgment above is the last independent one.

## Version 0.2.0 (2026-11-10)

Written for re-integration into HypeStake. All of it is new work in this repository; nothing was copied from the unlicensed pipeline or from HypeStake.

- Added TypeScript ports of the two scripts under `src/`, shared golden vectors under `vectors/` generated from the Python reference, and test suites in both languages that assert every vector.
- Fixed four defects in the Python scripts found while writing vectors (listed in `CHANGELOG.md`), and changed one behaviour on purpose: a post with no age is no longer treated as settled.
- Compared provider facts and identity rules with HypeStake source at commit `77a68e5c`, read only, and recorded the result in `references/hypestake-platform-map.md`. Plugin text was changed only where the platform source was stronger evidence; each such change says "checked against HypeStake source 77a68e5c". The STAR Finder kernel (`projects/hypestake-star/src/finder/`) was read for the field mapping and contact-rule comparison in `references/hypestake-integration-contract.md`. Its names were looked up by search; nothing was copied from it.
- Not verified in 0.2.0: no live ScrapeCreators call or spec fetch, no HypeStake test run, and no run of the kernels inside HypeStake's Vite, Deno or Render builds. The tool contracts in the integration contract are a proposal. The TypeScript port matches Python's Unicode `\w` with `\p{L}\p{N}_`, which agrees on every vector but may differ on characters a future Unicode version reclassifies.

## Verified here

- `scripts/contact_rules.py` and `scripts/creator_score.py` have unit tests that pass (`python3 -I -B -m unittest discover -s scripts/tests`), and the TypeScript ports pass every shared vector (`npm run verify`).
- ScrapeCreators paths, costs and the 197-path count were checked against `docs.scrapecreators.com/openapi.json` on 2026-11-02.

## Not verified

- No live API call was made. A 401 shows a route exists, not that it returns data.
- The unlicensed pipeline's own test suite was not run.
- Legal items marked Reported depend on secondary sources because primary pages were blocked. Counsel review is required before any outreach (see `skills/outreach-compliance`).
- Scoring weights, the 72-hour post-age cutoff and the confidence bands are judgment defaults, not research results. Calibrate them against deal outcomes.

## If you hold rights to the unlicensed pipeline

Say so. Its code and reference text could then be vendored with attribution instead of restated.

## Git history

Early commits on this branch (starting with 8df6bf4) contain a first version of `scripts/contact_rules.py`, its tests and the contact references that a reviewer judged to be near-copies of the unlicensed pipeline's code and text. The current files replace them, but history keeps them. Removing them needs a history rewrite and a force-push, which has not been done because it needs the owner's explicit decision. The two options are to rewrite the branch before it is merged, or to obtain a license grant from the pipeline's owner.
