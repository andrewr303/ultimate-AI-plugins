---
name: cold-outreach
description: "Draft one-to-one direct outreach for Andrew Rodriguez's freelance services outside the marketplaces: cold emails to founders, agencies, and finance teams; LinkedIn messages and connection notes; replies to Hacker News 'Who is hiring?' posts; referral asks to past colleagues; and short follow-ups that add something new, all compliant with CAN-SPAM for commercial email and with each platform's no-automation rules. Use for 'write a cold email to this company', 'LinkedIn message to this founder', 'reply to this HN hiring post', 'ask for a referral', or 'follow up on my outreach'. Never sends, bulk-messages, scrapes contacts, or automates LinkedIn. Not for Upwork proposals (proposal-writer) or existing clients (client-communications)."
---

# Cold outreach

One tailored message at a time, written for one real person, sent by Andrew himself. No bulk sends, no scraped lists, no automation of LinkedIn or any platform (`../../references/platform-rules.md`).

Read `../../references/andrew-profile.md` and `../../references/voice.md` (the "Cold outreach" guidance in the `ultimate-prose-andrew` skill when installed).

## Before drafting: marketplace gate

Ask Andrew, and check the ledger, whether the recipient or their organization first met him on Upwork or another escrow marketplace (PeoplePerHour, Arc, Fiverr, Freelancer.com, and similar). Run `python <plugin-root>/scripts/pipeline.py list --json` and read the `met_on` dates recorded with `pipeline.py add ... --met-on YYYY-MM-DD`; a missing date is not a "no", so ask.

- If they met on a marketplace less than two years ago, stop. Do not draft an email, LinkedIn message, or referral ask. Hand the request to `client-communications` for a message on that same platform. Upwork keeps those relationships on Upwork for two years unless the Conversion Fee is paid, and contact off the platform is circumvention that can restrict the account. (clm_up_010)
- The ROI calculator agency client met Andrew on Upwork. Contact that agency, and anyone Andrew met through that engagement, only on Upwork, including for referrals or testimonials.
- Relationships that started off the marketplace (LinkedIn, a referral, Hacker News) are not covered by this gate. (clm_up_012)

## Inputs

The recipient's name and role, the company, and a specific, verifiable reason to write that Andrew supplies or that comes from a public post he shares (a job post, a product launch, a hiring thread). If no specific reason exists, write an honest short introduction rather than inventing research or praise.

## Structure (about 50 to 150 words)

1. **Recipient-specific opening:** their problem or the post, not Andrew. No I-led opening, no "I hope this finds you well", no "I wanted to reach out".
2. **Connection:** one **Use** proof point that matches the reason (for example, the anonymized ROI calculator for a company with a spreadsheet-driven sales process).
3. **Offer:** a small, concrete first step (a scoped first milestone, a short call, a sample of how he would approach their model). Never a guarantee or a promised outcome.
4. **Ask:** one proportionate next step.
5. **Sign-off:** name, and for email the details CAN-SPAM requires (below). A portfolio link only if Andrew approved it.

Subject lines (email): specific and truthful, never deceptive or fake "Re:" or "Fwd:".

## CAN-SPAM checklist for commercial email (US)

For a message whose main purpose is promoting Andrew's services:

CAN-SPAM covers business-to-business email too; there is no B2B exception. (clm_cr_001)

- Accurate "From", "To", and reply-to; a subject line that reflects the content.
- A clear disclosure that the message is a business solicitation, for example a short line under the signature.
- A valid physical postal address (street address, registered USPS PO box, or registered private mailbox). Ask Andrew for it; never invent one.
- A clear opt-out (a reply works), honored within 10 business days, working for at least 30 days after sending, with no fee or extra information required. Never sell or transfer an opted-out address. (clm_cr_002, clm_cr_003)
- Penalties are assessed per violating email and are large (FTC figure in the claim ledger); outsourcing the sending does not move the responsibility. (clm_cr_004)

Keep a do-not-contact list in Andrew's own records; check it before drafting.

## Channel notes

- **LinkedIn:** one-to-one, relevant messages only. No sales pitch inside a connection invitation to a stranger. LinkedIn notes that promotional messages, even to one person, may fall under CAN-SPAM, and suggests labeling them as solicitations with a postal address. No sequences or automation tools (the User Agreement prohibits bots for messaging or connecting), and never exaggerate credentials. (clm_cr_005, clm_cr_006, clm_pl_006)
- **Hacker News "Who is hiring?":** reply only to posts Andrew is genuinely interested in, following the poster's stated contact method and format. One message per post; never mass-email from a parsed thread.
- **Referrals:** short, specific ask to someone who knows his work, naming the kind of project and making it easy to forward. Only after the marketplace gate above; a client met on a marketplace within two years gets any referral ask on that platform.

## Follow-ups

At most two or three, about a week or more apart, each adding something new (a convention, not a rule; on LinkedIn, no more than one polite nudge after no reply) (an answer, a relevant artifact, a sharper idea for their problem). then a short close-the-loop note. Stop immediately after an opt-out or a no. Never guilt or false urgency. (clm_cr_028) On marketplaces, Upwork discourages repeated contact before a contract, so do not follow up there.

## Output

The message, a subject line (email), word count, a "Confirm before sending" list (recipient details, approved links, postal address for email), and `python <plugin-root>/scripts/proposal_lint.py msg.txt --kind outreach --off-marketplace --allow-link <approved>` results. Contact details are expected in a direct email signature, so `--off-marketplace` reports them as INFO; never use that flag for a marketplace message.
