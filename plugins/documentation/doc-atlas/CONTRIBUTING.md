# Contributing

Keep the plugin focused on accurate, useful and visually coherent repository documentation. Skills should be independently discoverable, concise and actionable, with conditional details in references.

Use lowercase kebab-case skill names and matching `skills/<name>/SKILL.md` frontmatter. Keep referenced resources inside the plugin. Add a scenario to [evals/scenarios.json](evals/scenarios.json) when changing a workflow's trigger or operating boundary.

Helpers must remain read-only and offline, with no third-party runtime dependency. Preserve bounded traversal, secret exclusions, path containment, deterministic output and explicit coverage limitations. Test behavior at the boundaries instead of testing that text mirrors its implementation.

From the plugin root, run:

```sh
python -m unittest discover -s tests -v
python skills/repo-docs/scripts/repo_inspect.py --root .
python skills/repo-docs/scripts/docs_check.py --root . --path README.md
```

Parse manifest/frontmatter data and validate against the current Agent Plugins schema before packaging. Inspect the final archive: exactly one plugin root, all referenced files, no symlinks, credentials, caches or dependency trees. Rebuild the archive after any source change.

Document actual check outcomes. Component ingestion is separate from a live agent trial; neither proves every target repository or framework works.
