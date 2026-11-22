# Voice and delivery rules for client-facing writing

Every word a client, recruiter, or prospect will read is written in the freelancer's voice.

## Condensed rules (fallback, and the minimum in every case)

**Register.** the freelancer Business: calm, direct, specific everyday English, one level more controlled than conversation. Ordinary verbs, accurate nouns, contractions, short paragraphs of unequal length. The answer or practical point comes early, and a conclusion is tied to the mechanism, constraint, or consequence that makes it useful.

**Openings.** In proposals and cold outreach, open on the client's specific problem and a concrete approach or the most relevant proof. Do not open with "I", "I'm", the job title, "Dear Hiring Manager", "I read your job post", "My name is", or a warm-up such as "I hope this finds you well". Greet by first name only when the name is verified from the listing or the client's own feedback history; otherwise "Hi," or no greeting. In a reply inside a live thread, "I think" or "I can't make Friday" is fine.

**Pronouns.** "I" for the freelancer's own work. "We" only for a team the freelancer represents. Never imply a team.

**Claims.** Invent no numbers, results, clients, testimonials, credentials, availability, start dates, years of experience, badges, or links. Use only **Use** claims from the local profile; a **Confirm** claim becomes `[[CONFIRM: ...]]`; an **Internal** claim never appears. Keep the difference between a plan and completed work, a demo and a customer, a prospect and a client.

**Typography.** Straight quotes and apostrophes. No em dashes or en dashes as punctuation (use a comma, period, colon, or parenthesis). Preserve exact quoted strings, code, and required client keywords as given.

**Watchlist.** Scrutinize empty uses of: delve, tapestry, landscape, vibrant, pivotal, crucial, foster, bolster, garner, underscore, nuanced, multifaceted, intricate, meticulous, leverage, harness, realm, robust, holistic, seamless, streamline, comprehensive, spearheading, unlock, paradigm, game-changer, synergy, revolutionize, ecosystem, navigate, elevate, empower, genuinely, transformative, world-class; decorative moreover, furthermore, additionally; "at its core", "in today's world", "let's dive in", "it's important to note", "I wanted to reach out", "just circling back". A precise technical use (financial leverage, robust standard errors) is fine. Do not rotate synonyms to clear a list.

**Patterns to cut.** Staged reveals, rhetorical question-and-answer hooks, decorative "not X, but Y" pivots, manufactured triads, praise with no object, "perfect fit", guarantees, buzzword strings, a list of every technology the freelancer knows, apologies for being new to the platform, recap endings, motivational closers, "looking forward to hearing from you", "don't hesitate to reach out".

**Endings.** End on one proportionate next step or a decision the client can make. Proposals sign off with the confirmed name on its own line and nothing else.

## Delivery review (run before handing anything over)

1. Does the piece do the job for this reader, in the requested format and length?
2. Does every claim trace to a **Use** item, the freelancer's message, or the listing? Any invented specificity?
3. Were all client instructions followed (start word, keywords, questions, format)?
4. No contact details, off-platform suggestions, or unapproved links before a contract (`platform-rules.md`).
5. Does every sentence carry information, reasoning, action, or real human contact?
6. Run `python <plugin-root>/scripts/proposal_lint.py <file> --kind <kind>` (`<plugin-root>` is defined in the `freelance-legend` router skill) when Python is available and inspect each REVIEW finding in context. If it cannot run, write "Scan not run" and review by hand. A clean scan does not prove the writing is good.
