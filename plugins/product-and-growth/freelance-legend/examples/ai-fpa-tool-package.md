# Worked example: proposal package for "AI FP&A Tool Development"

Built from Andrew's apply-page screenshot of 2026-11-04 (job `~022118027855728317369`). The screenshot showed only the first paragraph of the description and no screening questions, so this package marks what is missing. It demonstrates the `proposal-writer` output; it has not been submitted.

```text
PROPOSAL PACKAGE: AI FP&A Tool Development · ID upwork:2118027855728317369
Status: Draft for Andrew's review. Not submitted.
```

## A. Fit and risks (internal)

- **Client's problem (their words):** "help complete the build of an AI-powered FP&A tool ... reviewing existing workflows, identifying gaps, and improving the tool to support better financial planning and forecasting ... comfortable with business metrics, financial data, and AI-driven processes ... collaborate closely and help refine the product for practical use."
- **Terms shown:** hourly, $25.00 to $50.00; Intermediate; less than 30 hrs/week; 1 to 3 months; Data Analytics category.
- **Verdict: Strong.** The listing asks for exactly the finance-plus-AI-software combination in the profile.
- **Angle:** where the AI may act versus where deterministic math must own the numbers, tied to the HypeStake valuation stack and his analyst background.
- **Gap:** the apply page warns Andrew does not meet the preferred location "United States, UTC-08:00". He is in the US on Mountain Time (one hour ahead of Pacific). It is a preference, so the proposal can go, but the client sees the mismatch; the letter states his time zone honestly and leaves working hours to `[[CONFIRM: working hours]]`.
- **Gap:** his profile has **no portfolio projects** and no certificates, and Upwork requires at least one portfolio highlight on a proposal (clm_up_027). Add an approved portfolio item (the anonymized ROI calculator is the best candidate, via `case-studies`) before submitting; it is a required item in section G.
- **Missing from the paste:** the rest of the description (the screenshot cuts at "less"), client details (payment verification, spend, hire rate, reviews), proposal and interview counts. Check them when opening the job.
- **Red flags:** none visible in the available text.

## B. Terms (paste into the form)

- Payment type: hourly
- Rate: $50.00/hr (the profile rate and the top of the client's range)
- Scheduled rate increase: none (leave off unless Andrew wants one; once agreed it is permanent for the contract)

Pricing workings (internal), from `price.py hourly --rate 50 --hours 15-20 --weeks 8 --fees 0.10`:

```text
$50.00/h x 15-20 h/week = $750.00-1000.00 per week
8 weeks: $6000.00-8000.00
Net rate: 10%: $45.00/h
Net figures are before income and self-employment tax.
```

The $45 floor is a gross bid rate until Andrew confirms whether he means gross or net (`andrew-profile.md`, "Rate floor"). A $50.00/hr bid clears that floor, and at the 10% fee the apply page showed (fixed for the contract) it nets $45.00/hr before income and self-employment tax. If Andrew decides the floor is net, $50 is the lowest bid that still meets it, so hold at $50 either way. The 15 to 20 hours a week fits inside "less than 30" and his stated 20 to 25 capacity: `[[CONFIRM: weekly hours]]`.

## C. Cover letter (paste-ready)

See `ai-fpa-cover-letter.txt` (229 words, 1,349 characters; `proposal_lint.py` reports 0 errors and one placeholder).

> Hi,
>
> An AI-powered FP&A tool earns trust when its forecasts can be traced and rerun, so the first thing I'd look at is where your current workflows let the model produce numbers and where plain calculation code should take over.
>
> That split is how I built the valuation features in HypeStake, a creator-brand deal platform I'm building as its solo founder and engineer: LLM research feeds structured inputs, and deterministic Python does the math, so every financial figure is reproducible rather than model-generated. Before that I was a financial analyst at a startup, building a five-year pro forma and revenue models, so the business metrics side is familiar ground.
>
> In the first week I'd review the existing workflows end to end, list the gaps that affect planning and forecast accuracy, and send you a short prioritized plan to approve before I change anything. After that I'd work through it with you in small, reviewable increments.
>
> Two questions that would shape that plan:
> 1. What is the tool built on, and where do today's forecasts come from (model output, spreadsheet logic, or code)?
> 2. Who uses it day to day, and which planning decision should it make easier first?
>
> I'm in Colorado on Mountain Time, one hour ahead of Pacific. [[CONFIRM: weekly hours and start date]] A short call here on Upwork would be a good next step.
>
> Andrew

## D. Screening answers

None were visible on the apply page. `[[CONFIRM: screening questions, if the full page shows any]]`

## E. Proof to attach

`[[CONFIRM: approved portfolio items]]`. Recommended once approved:

1. The anonymized spreadsheet-to-web ROI calculator (Python calculation logic, TypeScript front end, PDF output): closest proof of financial logic made into software.
2. A HypeStake valuation-features item (screens with synthetic data only): shows AI research feeding deterministic math.

## F. Connects and boost

- Base: 10 Connects ($1.50 at $0.15 each), charged on submission.
- Boost table at the time: 1st 18, 2nd 17, 3rd 16, 4th 3 Connects. First place needs 19 ($2.85).
- **Suggestion: boost 4 Connects ($0.60)** to take the fourth boosted slot, if it is still that low when he submits. The fit is Strong and the cost is small; boost Connects are charged only if the bid finishes in the top four or the client interacts with the proposal before the auction ends. Others can outbid him, and a boost cannot be adjusted after submitting. His call.

## G. Confirm before sending

- [ ] Weekly hours (proposed 15 to 20) and start date
- [ ] Screening questions, if the full page shows any
- [ ] **Required before submitting:** an approved portfolio item to add as a highlight (Upwork requires at least one)
- [ ] Rest of the job description: anything that changes the angle or the two questions
- [ ] Client details (payment verification, hire history, reviews) look credible

## H. If the client replies

Reply to a call request (adapt):

> Thanks, happy to talk. [[CONFIRM: two or three time slots, Mountain Time]] work for me, here on Upwork. If you can share a screenshot or short walkthrough of the current forecasting flow beforehand, I'll come with specific questions rather than general ones.

Likely questions:

- **"Have you built an FP&A tool before?"** Not one sold as FP&A software. The closest work is a spreadsheet-to-web ROI calculator for an agency client and the valuation features in HypeStake, plus a five-year pro forma and 60-month revenue model as an analyst.
- **"What would you do first?"** Map the current workflows and data sources, find where forecast numbers come from, and deliver a prioritized gap list for approval in the first week.
- **"Can you work Pacific hours?"** He is one hour ahead of Pacific; `[[CONFIRM: working hours]]`.

## I. QA log (internal)

| Check | Result |
| --- | --- |
| Truth | Every claim maps to a Use item: HypeStake solo founder and engineer; valuation stack pairing LLM research with deterministic Python math; analyst role with five-year pro forma and revenue models. Colorado and Mountain Time trace to the profile's identity facts ("At a glance", Location); working hours stay a placeholder |
| Client instructions | No special instructions visible in the available text |
| Platform rules | No contact details, no off-platform suggestion, no links |
| Math | `price.py` output above; net at the 10% fee shown on the apply page |
| Voice | Opens on the client's problem, not "I"; straight quotes; no dashes; no watchlist filler; ends on one next step and "Andrew" |
| Length | 229 words, 1,349 characters; opening sentence about 230 characters |
| Scan | `proposal_lint.py --kind cover-letter`: 0 errors, 1 INFO placeholder |
| Unresolved | Full description, client details, screening questions, portfolio item |
