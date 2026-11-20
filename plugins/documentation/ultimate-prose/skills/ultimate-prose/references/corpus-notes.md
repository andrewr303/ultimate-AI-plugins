# Corpus review and reproduction

The samples were reviewed locally for version 4.5. The skill contains aggregate observations, common phrases, and synthetic examples. It does not contain the source files, contact details, quoted threads, client names, or copied private messages, and none of the text was sent to an outside service.

## Inputs

Seven sent-email batches and one post database, supplied on 18 November 2026:

| File | SHA-256 |
|---|---|
| `sent_email_batch_001_012.md` | `81399bd72d9a270b9ac6c81f371c8816725d34b75bdc4af724aed3205ee5bdeb` |
| `sent_email_batch_013_024.md` | `1ffacd4f5f7a62b3413b30e5c0eac746c0bc1cf9951bbe8a78654f5621c81991` |
| `sent_email_batch_025_036.md` | `a70c8e86a72efa323d01ee1cccd7a68f9e270232d8bbd8fe836cf4724229a36f` |
| `sent_email_batch_049_060.md` | `98a2f17babbbdda163b168dddd72f2b031b86eea4a935698b512b567f1ea927a` |
| `sent_email_batch_073_084.md` | `8a34e333899244ce8aeea70948cd59e35a9c326b9e7cf4382c3a4600a2904abb` |
| `sent_email_batch_085_096.md` | `bc74067bac10c89102a80ab40dc32ec2fda56aa3ae69caa24629cdbcfec061b1` |
| `sent_email_batch_097_109.md` | `6726112ad49b71bd8d8e46b556833c64b7cd67e540e9ad7a496b6781e7c75ce8` |
| `Tweet_Database_..._all.csv` | `ecd0c4713b23c122d89bd68d1c7836aab97951c02f07ea0cf863bcc8f52a28c5` |

Batches 037 to 048 and 061 to 072 were not supplied, so 24 emails in the numbered range are absent.

## Email extraction and counts

Each record keeps only the newest message: text before a reply or forward header, a quoted-history line, an "On ... wrote:" line, or a rule of underscores. Inline quotations of other people, image placeholders, mail-client footers, and bare links are removed. The greeting and sign-off are recorded and then removed before sentence measurements.

- 85 records dated 14 September to 11 November 2026; 66 carry quoted history. 80 contain his own prose, about 9,900 words. The other five are calendar acceptances or a forward with no text.
- Length: median 61 words, quartiles 18 and 171. Sixteen are 15 words or fewer, 24 are 16 to 60, 24 are 61 to 200, and 16 exceed 200.
- Sign-off: "Best regards," followed by his full name in 75 of 80, "Thanks," in one. The rest are phone replies with no sign-off.
- Greeting: 8 of the 40 emails at 60 words or fewer have one; 29 of the 40 longer emails do. Forms: "Hi <name>," 21, a bare first name 8, "Hi all" or "Hi everyone" 6, "Hey <name>," 2.
- Sentences (rough regex estimate): mean 18.9 words overall, 19.6 in emails over 60 words, 13.7 in shorter ones, 17.9 in the 15 emails sent to client-side recipients. Eighteen percent of sentences are 8 words or fewer and 12 percent are 30 or more. Prose paragraphs average 2.1 sentences; nine in ten have four or fewer.
- Per 1,000 words: contractions 34 (21 to client-side recipients), question marks 4.6, exclamation marks 1.8 (11 in the shorter emails), parentheticals 2.4, semicolons 0.4, em or en dashes 0.1.
- Sixty-three emails have no exclamation mark, 16 have one, and one has two. Thirty-four ask at least one question.
- First-person forms open about 27 percent of sentences. "Yes" opens 14 percent of sentences in the shorter emails.
- Serial comma in 35 lists of three, omitted in 8. Curly apostrophes appear in 66 places against 272 straight ones, consistent with a phone mail client.

## Post extraction and counts

Only the `Tweet` column is measured, without a leading handle. `Original Post Text` and its author are other people's writing and stay out of the voice evidence. `Notes` and `Variation Chosen` record how each post was produced.

- 93 rows, all marked Live, posted from 30 September to mid-November 2026: 91 replies and 2 original posts. Every `Andrew Rating` field is blank.
- 40 rows are `Custom`: his own text, or his edit or combination of drafted options. 46 are a drafted option (A, B, or C) that he picked; the notes on 21 of those record an edit or an added sentence. 7 have no recorded origin.
- `Custom` rows: median 49 words, mean sentence 14.4 words. Per 1,000 words, first-person words 20.9 against 11.8 in drafted picks, plain emphasis words 11.9 against 0.5, exclamation marks 2.5 against 0.5.
- No em dash, en dash, emoji, or hashtag appears in any of the 93 posts.

## Evidence roles

| Evidence | Use | Limit |
|---|---|---|
| A live correction from Andrew | Apply it to this task | Do not generalize beyond its scope |
| Quick email replies; `Custom` posts; sentences a note says he added | The strongest evidence of his own phrasing | Small samples, one period |
| Longer, formal emails | Structure, moves, and what he sends under his name | May have been drafted with assistance |
| Drafted options he picked unedited | What he approves of | Not his wording |
| Quoted history and original posts | Context only | Never voice evidence |

## Scanner calibration

`lint_andrew.py` was run over the 80 email bodies and the posts before and after its 4.5 changes. Findings other than the stated straight-quote preference fell from 104 to 54 on the emails, and from 22 to 6 on the 40 `Custom` posts. The changes are listed in `validation.md`. This shows the scanner now contradicts his sampled writing less; it does not show that the scanner recognizes his voice.

## Limits

Sentence figures come from a regex splitter and move with abbreviations, lists, and fragments. Counts are per message, not per paragraph. The emails come from one client project and one working relationship over two months, and the posts are nearly all replies on related subjects. The sample cannot establish an ideal sentence length, an authorship fingerprint, a favorite wording, or a cause of engagement. No sample establishes unassisted authorship.

## Earlier inputs

Versions 4.0 to 4.2 used a 17-row email CSV and a 20-row export of the same post database, plus three narrative profiles recorded in `personalization.md` and `voice-calibration.md`. Their aggregates and reproduction script are in the 4.2 review bundle. The 4.5 measurements replace those figures; the earlier profile's Reddit corpus was never supplied and is not used.
