---
name: profile-optimizer
description: "Write and tune the freelancer's freelance profiles so the right clients find and trust him: Upwork title, overview, skills, hourly rate, portfolio order, and Project Catalog offers; LinkedIn headline, About, and Service Page; Contra, Toptal, Braintrust, Arc, and other platform profiles; Fiverr gigs and other gig listings; and a reputation plan for Job Success Score and Upwork badges. Use for 'fix my Upwork profile', 'write my overview', 'what should my title be', 'set up Project Catalog', 'LinkedIn service page', 'set up a Fiverr gig', or 'how do I get Top Rated'. Not for single proposals (proposal-writer) or long-form case studies (case-studies)."
---

# Profile optimizer

Profiles are searched and skimmed. The job is to make the finance-plus-software combination obvious in the first lines, with proof he can back up.

Read `<data-dir>/profile.md`, `../../references/platform-rules.md`, `../../references/voice.md`, and `<data-dir>/approved-proof.md` (the live approval record, including approved testimonials; `<plugin-root>` and `<data-dir>` are defined in the `freelance-legend` router). Ask the freelancer to paste his current profile text first; never fetch it.

## Upwork main profile

Specialized Profiles were removed on 2026-05-28, so there is one main profile. Upwork now surfaces the portfolio items most relevant to each client automatically, which favors one broad, keyword-rich profile with varied portfolio items over narrow positioning.

- **Title:** a client-language phrase that names the combination, for example "Full-Stack Engineer for Financial Tools | Next.js, Python, AI". Draft three options; keep within Upwork's field limit (check the live form).
- **Overview:** first two lines carry the hook clients see before "more": who he helps and what he builds, in their words. Then proof (profile **Use** wording only), the kinds of projects he takes, how he works (spec first, funded first milestone, tested math), and a closing line inviting a message on Upwork. No contact details, no links to pages that expose them, no claims of years, badges, or results he has not earned.
- **Skills:** the stack and domains clients actually search: React, Next.js, TypeScript, Supabase, PostgreSQL, Python, FastAPI, Node.js, LLM integration, OpenAI API, Anthropic Claude, financial modeling, FP&A, Excel, ROI calculator, dashboard, MVP development. Order by the work he wants most.
- **Rate:** the profile rate signals positioning. Show `python <plugin-root>/scripts/price.py gross` for the net he wants after the fee range.
- **Portfolio:** only items in `<data-dir>/approved-proof.md`; hand drafting to `case-studies`. Quote a client only from that file's Testimonials table, word for word, with the attribution recorded there. Order the strongest finance-plus-software item first.
- **Project Catalog:** up to 20 live projects, each with up to three tiers, add-ons, and five search tags. Good candidates: an Excel-to-web ROI or pricing calculator, a startup financial model with dashboard, a Next.js and Supabase MVP sprint, an AI feature integration. Price each tier with `pricing-scoping` so it clears the rate floor after fees. Catalog projects must be created in the Upwork UI (not through MCP).

## Reputation plan (Upwork)

Explain the official mechanics from `platform-rules.md` without promising outcomes: JSS uses the best of 6-, 12-, and 24-month windows, weights higher-earning contracts, and is hurt by negative feedback on unpaid contracts; badges have published thresholds; off-platform behavior loses badges for six months. Practical advice: prefer clients with hiring history and fair reviews (`job-vetting`), scope tightly, deliver through funded milestones, and ask for feedback the way `client-communications` describes.

## Other platforms

- **LinkedIn:** headline (who he helps plus the combination), About (problem-first, short paragraphs), Featured items from approved proof, and a Service Page listing finance-plus-software services. LinkedIn work is paid off-platform, so pair it with `contracts-scope` for an SOW and deposit. No automation of messages or connection requests.
- **Fiverr:** gigs written offline for the freelancer to paste: a client-language title, a description that follows the overview rules above, three package tiers priced with `pricing-scoping` (gross-up from the 20% seller fee, which is **unverified**, so label those prices as an assumption until the freelancer reads the fee in his seller dashboard), and FAQ answers. No contact details, and no payment off Fiverr.
- **Contra:** project-based profile with case-study style projects (0% freelancer commission per `platform-rules.md`).
- **Toptal, Braintrust, Arc, Gun.io:** application profiles that stress shipped full-stack work and AI integrations; for Toptal, add a prep checklist for its multi-stage screening. On Arc, compensation is never discussed with clients.

## Output

For each profile: the paste-ready text per field, a short "why" line per choice, character counts where the platform limits them, and a "Confirm before publishing" list. Run `python <plugin-root>/scripts/proposal_lint.py overview.txt --kind profile-overview` and fix every contact-detail or link error before the freelancer publishes.
