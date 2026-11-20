# Creator Intelligence

Creator Intelligence takes a niche and returns a vetted shortlist of creators, each with the business contact they chose to publish. It uses public data only and never sends a message.

It merges two packs: ScrapeCreators' social research skills (MIT) and the creator-discovery method from `tigerless-labs/influencer-discovery`, restated in new wording because that repository has no license (see the history caveat in `PROVENANCE.md`). Research added the parts neither pack had: a scoring rubric with gates and confidence labels, a compliance gate for scraping and outreach, and corrected API facts. See `PROVENANCE.md` for sources and what was not verified.

## Try it

After installing from the [host guide](../../../docs/hosts.md), open your target project and select [`creator-research`](skills/creator-research/SKILL.md). Try this prompt.

> Build a shortlist of five makers who post about woodworking. Record why each fits and link to their public business-contact source when available.

## Pipeline

```
define -> discover -> capture contact -> vet -> hand off
```

Start with `creator-research`. It fixes the three decisions every run needs (how many, what counts as qualified, what to prioritise), defines the candidate record, and routes to the stage skill.

| Skill | Job |
|---|---|
| `creator-research` | Router, record format, status vocabulary, run report |
| `creator-discovery` | Find creators who bring their own audience |
| `creator-contact-capture` | Get the contact the creator published, and tell a creator's site from a product site |
| `creator-vetting` | Gates plus an eight-dimension score with a band and a confidence label |
| `outreach-compliance` | Source policy, pre-send gate, polite fetching, injection boundary, questions for counsel |
| `outlier-post-finder`, `comment-mining`, `transcript-intelligence`, `competitor-social-research`, `ad-library-teardown`, `trend-discovery`, `social-listening-brief`, `product-demand-research`, `content-repurposing` | Research workflows around a creator or niche |
| `scrapecreators-api` | Endpoint routing, credit costs and known gaps, checked against the live spec on 2026-11-02 |

## Setup

Metered sources need a ScrapeCreators key in the environment:

```bash
export SCRAPECREATORS_API_KEY=sk_...
```

Nothing else is required. Free routes (creator sites, podcast feeds, newsletter feeds, Mastodon and Bluesky public endpoints) need no key. Never write a key or a creator's contact data into this repository.

## Scripts and kernels

The Python scripts are the reference the skills call from a shell. Both are standard-library Python with unit tests:

```bash
python3 -I -B -m unittest discover -s scripts/tests
```

`src/contact-rules.ts` and `src/creator-score.ts` are TypeScript ports for HypeStake's browser, Deno Edge and Node Render runtimes: pure functions, ES2020 library, relative `.ts` imports, no Node built-ins. The shared golden vectors in `vectors/` are generated from the Python reference by `scripts/build_vectors.py`, and both test suites assert every vector, so the two cannot drift. To check everything (typecheck, TypeScript tests, Python tests, the kernel runtime floor and Markdown links), from this directory:

```bash
npm install
npm run verify
```

After a reviewed behaviour change, change both implementations, then run `python3 -I -B scripts/build_vectors.py --write` and read the vector diff before committing.

- `scripts/contact_rules.py` decides whether an address found on a page belongs to the creator. It keeps personal addresses and creator-published deal inboxes on the creator's own domain, and rejects role, legal, placeholder, platform and repeated footer addresses.
- `scripts/creator_score.py` computes median-baseline outlier lift and the creator score. Missing dimensions are renormalised, never scored as zero, and cap confidence at low. Posts with no age or no metric value are left out and counted. The creator score is not HypeStake's Match Score: it describes one creator against one brief and never recommends accepting a deal.

## HypeStake

This plugin is meant to be re-integrated into HypeStake's AI features. Two references prepare that:

- [`references/hypestake-platform-map.md`](references/hypestake-platform-map.md): vocabulary, and where the plugin's ScrapeCreators and identity facts agree or disagree with the platform source.
- [`references/hypestake-integration-contract.md`](references/hypestake-integration-contract.md): field mapping to the STAR Finder kernel and the Creator Finder v2 contract, contact-rule conflicts, proposed tool contracts and the boundary rules a platform caller must keep.

## Limits

The scoring weights, the 72-hour post-age cutoff and the confidence bands are judgment defaults. Calibrate them against deal outcomes before treating the score as predictive. The legal findings are engineering research, several from secondary sources, and counsel should review them before any outreach.
