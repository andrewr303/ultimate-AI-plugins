# README planning worksheet

Use this worksheet to decide content. Remove empty sections rather than preserving a template shape.
The bracketed fields below are authoring prompts; none belongs in a delivered README.

## Evidence checklist

| Reader question | Inspect | Record |
| --- | --- | --- |
| What does it do? | Entrypoint, representative example, tests | Observable input and result |
| Can I run it? | Runtime declarations, lockfile, CI | Supported version and prerequisites |
| How do I install it? | Release/package config and current docs | Real distribution and install command |
| What is first success? | Small safe example | Command, working directory, expected behavior |
| What does it not cover? | Validation, guards, known limitations | Concrete boundary and next action |
| Where do I go next? | Existing docs and contribution files | Real reader-oriented destinations |

Keep facts with source locations during drafting. This worksheet is not a substitute for inspecting them.

## Possible document shape

```markdown
# [Real project name]

[One sentence: user, action, useful outcome.]

[Optional real product image with descriptive alt text.]

[Optional short row of verified badges.]

## Get started

[Prerequisites and the first useful task.]

[The actual installation and minimal example.]

[Expected behavior, qualified by how it was verified.]

## What you can do

[Two to four concrete capabilities, demonstrated with real examples.]

## Choose your next step

| Goal | Guide |
| --- | --- |
| [Reader goal] | [Existing guide with a descriptive link] |

## Configuration

[Only the settings needed for the first task; link deeper reference.]

## Limits and troubleshooting

[Known boundaries; symptom and correction where supported.]

## Contribute

[Link the actual contribution guidance. Omit if absent and outside scope.]

## License

[Link the actual license file without inventing terms.]
```

A CLI may need a compact command example above the screenshot.
A visual application may benefit from a screenshot before the quickstart.
A library should show a realistic import and minimal result.
An internal service should explain local prerequisites and how to verify readiness.
A small utility can omit most sections and link its reference from the quickstart.

## Badges and assets

- Verify the repository, branch, workflow, package, or release encoded by every badge URL.
- Link a status badge to the underlying check or release, not an unrelated homepage.
- Prefer information that affects a user's decision; stars rarely explain operation.
- Use relative paths for repository-owned assets and descriptive stable filenames.
- Keep an image's source state and version in the draft notes when accuracy depends on them.
- Provide copyable text for an image that conveys a command, status, or critical result.
- Do not fabricate a screenshot because the runtime is unavailable.

## Completion record

Record files changed, facts source-reviewed, examples executed, links checked, renderers viewed,
and exact gaps. A source-reviewed example and an executed example are different statuses.
