# Developer reference worksheets

Use these planning structures selectively. Bracketed prompts are not finished documentation.

## Source map

| Contract area | Owning source | Example/test | Version | Status |
| --- | --- | --- | --- | --- |
| Operation | Schema pointer or symbol | Relevant fixture/test | In-scope version | Confirmed, inferred, or unknown |
| Authentication | Security config/schema | Auth test | In-scope version | Known mechanism and gaps |
| Error behavior | Handler/type/schema | Failure test | In-scope version | Known cases only |
| Pagination | Query/response contract | Boundary test | In-scope version | Stop condition and ordering |

A schema pointer can identify an operation or model; include its source file and revision in working notes.
Avoid adding noisy internal implementation references to every public paragraph.

## Operation page shape

```markdown
# [Action-oriented operation title]

[Purpose and the situation in which it helps.]

## Request

[Real method/path or public symbol and required auth.]

| Input | Location | Type | Required | Meaning and constraints |
| --- | --- | --- | --- | --- |
| [Actual name] | [Actual location] | [Actual type] | [Actual status] | [Evidence-backed meaning] |

## Example

[Minimal valid request and a consistent response, using fictional data.]

## Result

[Success shape, optional/null behavior, and fields useful for the next task.]

## Errors

| Condition | Result | Recovery |
| --- | --- | --- |
| [Known trigger] | [Actual documented result] | [Supported next action] |

## Related tasks

[Existing guide links, pagination rules, or relevant model definitions.]
```

Omit sections without evidence. A short CLI option may fit in a reference row instead of a page.

## CLI reference fields

- Canonical command, aliases, and subcommands from parser registration.
- Positional arguments, cardinality, required options, and mutually exclusive groups.
- Defaults and precedence between flags, environment variables, and config files.
- Working directory, stdin/stdout behavior, output formats, and exit codes when established.
- Side effects and external-service requirements relevant to safe use.
- One realistic success path and a known failure with recovery.

## Compatibility review

Before changing a renderer, record its installed version, the source schema version,
public URL base path, stable operation identifiers, custom components and plugins,
search integration, security defaults, build command, and local fixture coverage.
Keep that record in working notes; do not expose internal implementation details in the user flow.

## Verification record

| Check | Result | Scope |
| --- | --- | --- |
| Source/schema agreement | Pass, fail, or untested | Exact operations inspected |
| Example validation | Pass, fail, or untested | Exact fixtures and schema version |
| Generator build | Pass, fail, or unavailable | Tool/version and command |
| Rendered review | Reviewed or unavailable | Pages, viewport and theme |
| Live API request | Not performed or explicitly authorized result | Exact environment and side effects |

A schema-valid example may still describe behavior the server does not implement.
An executed request proves only its actual inputs, environment, and observed result.
