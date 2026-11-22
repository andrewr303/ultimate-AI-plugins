---
name: pricing-scoping
description: "Scope and price a freelance job for the freelancer with transparent, script-checked math: bottom-up task estimate, his doubled-hours method at his rate, comparison with the client's budget, effective hourly rate, net after platform fees, hourly vs fixed recommendation, milestone splits that sum exactly, phased offers when the budget is short, and scheduled rate increases. Use for 'how much should I bid', 'is this budget realistic', 'split this into milestones', 'hourly or fixed?', 'what do I net', or a price check inside a proposal. Not for writing the cover letter itself (proposal-writer) or negotiating with a client who already replied (client-communications)."
---

# Pricing and scoping

Every number comes from `python <plugin-root>/scripts/price.py` (`<plugin-root>` is defined in the `freelance-legend` router) with its inputs shown, so the freelancer can check it. If Python is unavailable, show the arithmetic line by line and say the script was not run.

Read `<data-dir>/profile.md` (rate, capacity, payment preferences) and the fee and Connects facts in `../../references/platform-rules.md`.

## Method

1. **Scope the whole ask.** List tasks with low and likely hours. Always consider setup and access, discovery or spec confirmation, the core build, integrations, data migration, testing, revisions, deployment, documentation, and handoff. Name anything the listing leaves ambiguous as an assumption, not a task.
2. **Estimate method.** Double the likely hours, then multiply by the confirmed rate. Show raw and doubled totals.
   ```bash
   python <plugin-root>/scripts/price.py estimate --task "Spec and data review:3:4" --task "Calculation engine:8:12" \
     --task "UI and charts:8:10" --task "Testing and reconciliation:3:5" --task "Deploy and handoff:2:3" \
     --rate 50 --budget-fixed 2000 --bid 2000
   ```
   For an hourly listing use `--budget-hourly 25-50`. Pass `--fees 0.10` when the apply page shows a specific fee; the default prints 10% and 15% cases. `--bid AMOUNT` adds the net at the amount the freelancer will actually bid. The text output labels each net with the amount it applies to (the client's budget, the bid); quote the net for the number being bid, never the net on the doubled price. Add `--json` before or after the subcommand for machine-readable output.
3. **Compare with the budget.** State the client's budget, the doubled-method price, the ratio of doubled price to budget, and the effective rate at the budget on both planned and raw-likely hours, gross and net of each fee. The script warns when the budget falls below the rate floor.
4. **Recommend a bid** in one sentence with the reason. the freelancer prefers a price he can defend over losing a deal to an unreasonable number. `estimate` prints a recommendation line using this rule:
   - If the effective rate at the budget on raw likely hours is at or above the floor: **bid within the budget with a stated scope**, and note the doubled figure.
   - Otherwise, if the doubled price is more than 1.5 times the budget: offer a **narrower first phase** that fits the budget and proves the core (name what is out of scope), or the **full price with a short explanation** of what drives it.
   Use the floor confirmed in the local profile. The script reports its own example threshold separately.
5. **Hourly vs fixed.** Prefer hourly when scope is open-ended, the client wants ongoing collaboration, or discovery is incomplete; fixed by milestone when deliverables are crisp. On hourly, propose a weekly range inside his stated capacity (`[[CONFIRM: weekly hours]]`) and a first-phase total:
   ```bash
   python <plugin-root>/scripts/price.py hourly --rate 50 --hours 15-20 --weeks 6
   ```
6. **Milestones (fixed).** Two to four. Milestone 1 is about 10 to 25 percent, funded before work starts, and delivers something reviewable. Each has a deliverable, how the client knows it is done, an amount, and a relative due day. Amounts must sum exactly:
   ```bash
   python <plugin-root>/scripts/price.py milestones --total 2400 --split 15,45,40 --days 7,21,35 \
     --names "Confirmed spec and calculation prototype|Working app with charts|Tested release and handoff"
   ```
   Every split value must be above zero. Amounts round to whole dollars, so each row shows the actual percent of its rounded amount; paste that percent, not the nominal split.
7. **Scheduled rate increases (new hourly proposals, optional).** Only when the freelancer asks. Upwork lets a freelancer propose a scheduled increase on an hourly proposal; check `platform-rules.md` for the current rule and tell the freelancer the term cannot be changed after he accepts an offer. Raising the rate with an existing client is a message, so it goes to `client-communications`, which takes the new rate from `price.py`.

## Platform fees and gross-up

Read the fee from the apply or offer screen when the freelancer has it; otherwise use `../../references/platform-rules.md` (Upwork 0 to 15% per contract and locked once sent; Fiverr 20% (**unverified**; check the seller dashboard); Freelancer.com 10%; PeoplePerHour tiered per buyer; Contra 0% for freelancers; several others unverified). To net a target, gross up instead of guessing:

```bash
python <plugin-root>/scripts/price.py gross --net 45 --fee 0.10
```

When a gross-up uses an unverified fee (Fiverr, or any fee not read from the freelancer's own screen), label the result as an assumption in the output.

On Fiverr and Project Catalog packages, set tier prices from the gross-up so each tier still clears the rate floor after fees. On Gun.io the client sees one total that already includes the platform fee. On Arc, never discuss the freelancer's compensation with the client.

## Output

```text
Recommendation: <bid and structure> because <reason>.
Workings (internal): price.py output
Assumptions: <scope assumptions to confirm or state in the letter>
Out of scope for this price: <items>
Net to the freelancer: <fee cases, each labelled with the amount it applies to>
Net figures are before income and self-employment tax; check set-asides with his accountant.
```

## Guardrails

- A budget that "will increase later" or "for the right person" is not compensation evidence.
- Unpaid "test tasks" that are real deliverables are a red flag (see `job-vetting`). A small paid trial milestone is fine.
- Never promise savings, revenue, rankings, or deadlines that depend on the client.
- Capacity and start dates are always `[[CONFIRM]]` items.
