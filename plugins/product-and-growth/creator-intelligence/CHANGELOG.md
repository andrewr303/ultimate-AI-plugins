# Changelog

## 0.2.1 (2026-11-10)

- Add `.claude-plugin/plugin.json` so the plugin has a Claude Code manifest that agrees with the root `plugin.json`; set author in both.
- `scripts/creator_score.py`: malformed stdin (not JSON, missing keys, non-numeric score, `gates` given as a string) now prints one error line and exits 2 instead of a traceback. Added CLI tests for this.

## 0.2.0 (2026-11-10)

Prepares the plugin for re-integration into HypeStake.

### Added
- TypeScript ports of the two scripts: `src/contact-rules.ts` and `src/creator-score.ts`, exported from `src/index.ts`. Pure functions, ES2020 library, relative `.ts` imports, no Node built-ins and no regex lookbehind.
- Shared golden vectors in `vectors/`, built from the Python reference by `scripts/build_vectors.py`, and asserted by both `scripts/tests/test_vectors.py` and `test/vectors.test.ts`.
- `package.json`, `tsconfig.json` (ES2020 library, kernels only) and `tsconfig.test.json`. `npm run verify` runs the typecheck, the TypeScript tests, the Python tests, a runtime-floor check of `src/` and a Markdown link check.
- `references/hypestake-platform-map.md` and `references/hypestake-integration-contract.md`.
- Candidate record fields `sources[]` and `degraded[]` for provenance.

### Changed
- `creator_score.outlier_report`: a post with no `age_hours` is now left out of the baseline and counted as `excluded_unknown_age`, instead of counting as settled. A post with no metric value is counted as `excluded_missing_metric` instead of `excluded_too_young`. The report always has all three counts. The command line accepts `min_age_hours`.
- `creator_score`: sums are plain left-to-right loops, so results do not depend on the Python version's float summation. Inputs are validated: booleans, strings, NaN and negatives raise `ValueError`.
- `contact_rules.decode`: a pinned entity decoder (numeric entities and eight named entities) replaces `html.unescape`; surrogate and out-of-range escapes stay as written.
- Skill and reference text: HypeStake nouns, the creator score is described as not a Match Score, the vetting report's "Recommendation" is now "Next research step", and the ScrapeCreators facts named in the platform map were corrected.

### Fixed
- `contact_rules.extract` and `extract()` in TypeScript ran in quadratic time on a long run of address characters (about 0.7 s for 40,000 characters of `a%`). Every quantifier is now bounded (local part 64, labels 63, at most 127 labels) and a domain over 253 characters is dropped, so the scan is linear: a few milliseconds for 200,000 adversarial characters. Tests in both languages pin it.
- The characters that block a match before an address depended on each engine's Unicode tables (U+0C5C before an address: Python extracted it, Node did not). Now only ASCII decides: a local-part character or any non-ASCII character just before a candidate blocks it, in both languages. The domain end also refuses `_` and any non-ASCII character, matching the STAR Finder kernel's `hs-finder-ts-1.0.1` lookahead.
- `classify` and `is_roster_page` consumed a generator argument while validating it, so `platform_domains=(d for d in ["youtube.com"])` let `jane@youtube.com` through as `personal`. Iterables are now materialised once.
- `creator_score` raised `OverflowError` on a huge integer such as `10**400`; it now raises the documented `ValueError`. Post ids must be a string, null or a whole number of at most 2**53 - 1 (larger numeric ids collapsed in JavaScript), and NaN and infinite ids are refused in Python as in TypeScript. `__proto__`, `constructor` and `prototype` are refused as metric names in both.
- `roundHalfEven1` (TypeScript) is exact only for |x| <= 1e9 and now throws `RangeError` outside that bound. Scores never leave 0 to 100.
- `contact_rules.extract` cut a longer domain short: `jane@janedoe.com2` and a 26-letter top-level label returned a plausible but wrong address. A match must now end where the domain ends. The trade-off in recall: `a@b.com-`, `a@b.com.x` and `a@b.com.5` now return nothing, while `a@b.com.` at the end of a sentence still returns `a@b.com`.
- `contact_rules.classify` kept addresses no extraction could produce: `a@b@janedoe.com`, `jane@janedoe.com/x`, `jane@10.0.0.1`, `.jane@janedoe.com` and a trailing-dot domain were `personal`. They are now `reject_junk`.
- `contact_rules.registrable_domain` returned `co.uk` for a bare suffix and accepted URLs, ports and non-ASCII labels as hosts. They now return `None`.
- `creator_score.outlier_report` raised `TypeError` on `"age_hours": null` and omitted `excluded_too_young` when no post was settled.

## 0.1.0

- First release: 15 skills, contact attribution rules and creator score scripts.
