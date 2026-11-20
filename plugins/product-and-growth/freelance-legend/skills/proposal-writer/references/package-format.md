# Proposal package format

Return one package per job. Keep internal notes out of the paste-ready sections so Andrew can copy each section straight into the form.

```text
PROPOSAL PACKAGE: <job title> · ID <normalized job ID>
Status: Draft for Andrew's review. Not submitted.

A. Fit and risks (internal)
   Verdict, angle chosen, red flags, gaps (including any "preferred qualifications" warning),
   and what would change the recommendation.

B. Terms (paste into the form)
   Payment type: hourly | fixed by milestone | fixed by project
   Rate or bid: $___
   Milestones (fixed price):
     1. <deliverable and done-signal> · $___ · due Day __
     2. ...
   Duration: <form option>
   Pricing workings (internal): price.py output (task table, raw and doubled hours,
   price, budget comparison, effective rate, net after fee).

C. Cover letter (paste-ready)
   <text>
   (<words> words, <characters> characters)

D. Screening answers (paste-ready)
   Q1: <question verbatim>
   A1: <answer>

E. Proof to attach
   Up to three approved items, one line each.

F. Connects and boost
   Base Connects, suggested boost, dollar cost, reasoning.

G. Confirm before sending
   - [ ] every [[CONFIRM: ...]] placeholder, one per line

H. If the client replies
   Adaptable reply and likely questions with short supported answers.

I. QA log (internal)
   Each quality-gate check with pass/fix notes, proposal_lint.py result or "Scan not run",
   and anything unresolved.
```

On `final`, return only B (without workings), C, D, and E with edits applied and no placeholders. If a placeholder is still unresolved, list it instead of guessing.
