# Content, localization and change notes

## Establish canonical content

Inspect repository metadata conventions, existing localizations, current version and supported platform. Keep the canonical directory layout rather than inventing a new store schema. A previous fastlane layout and a current asc metadata layout may require an explicit migration; inspect help/schema and preserve a baseline before conversion.

If asc is available, start with its installed metadata/localization help and exact leaf schema. Resolve app/version/localization IDs from verified reads. A generic app name or default environment ID is insufficient when several apps match. Pulling metadata is a read from the service but a local write; use an agreed output location and avoid overwriting hand edits unknowingly.

Separate app-level information, version-level text, promotional text, review notes, subscription descriptions and in-app event content. Each has different scope and validation. Do not place reviewer credentials in a public description or generated changelog.

## Write from real evidence

Use actual commits, accepted issue descriptions, supplied release bullets and implemented user-facing behavior. Exclude internal refactors unless they meaningfully affect users. Do not promise fixed bugs, performance gains, compatibility, awards, pricing, privacy or security behavior without evidence. Group related changes into readable short notes and keep known limitations when relevant.

A changelog is a draft until its claims are checked against the intended binary/version. Avoid leaking commit metadata, internal ticket links or private implementation details into store copy. Preserve the user’s tone and established terminology without copying another product’s claims or visual identity.

## Localization workflow

Identify source locale and approved glossary. Translate intent and product terminology; preserve placeholders, brand names, supported formatting and meaningful constraints. Track source text, translated text, locale, reviewer status and unresolved ambiguity. Machine-generated translation is not human approval.

Validate placeholder count/type/order where the format requires it. Check plurals, truncation, right-to-left layout, number/date conventions and text rendered in the actual app/screenshot when relevant. Avoid deleting a locale merely because a local file is absent. A missing translation should be explicit rather than silently copied into every locale.

For app string catalogs, distinguish in-app `.xcstrings` review from store listing metadata. The simulator source’s localization audit is a useful concept, but source extraction and placeholder heuristics do not prove every runtime string is translated.

## ASO as evidence, not guarantees

Inspect title/subtitle/keyword relevance and duplication, product fit and locale intent. Respect current field limits verified from official specs/tool validation. Do not invent search volume, rankings or conversion lift. If an optional keyword service is available and authorized, record the observation window, source, territory and limits; otherwise provide a qualitative audit.

Do not add competitor/trademark terms or unsupported superlatives solely to maximize keyword coverage. Treat search suggestions and recommendations as hypotheses, not proof that a keyword will perform.

## Apply carefully

Prepare a field-level diff per locale and a dry-run plan when supported. Resolve deletes and locale fallbacks explicitly; preserve unrelated content. Execute scoped remote edits when the task includes them, then read back fields to distinguish saved, submitted and publicly visible states. Metadata preparation alone does not authorize review submission.
