# Doc Atlas starter verification

The starter packages Doc Atlas 1.0.1. Each row reports the observed stage for
this package. Install and manifest checks establish host discovery or package
structure. A separate session run is needed to observe model-level invocation.

| Host or check | Installed or discovered | Skill invoked | Output verified |
| --- | --- | --- | --- |
| Codex CLI 0.171.0 | Installed and enabled from the extracted starter in a temporary Codex home | Not run | Not run |
| Claude Code 2.1.330 | Strict manifest validation reported eight skills | Not run | Not run |
| Kimi Code | Native manifest checked by the catalog validator | Not run | Not run |
| ChatGPT desktop and web | Not run | Not run | Not run |
| OpenCode, Gemini CLI, other Agent Skills hosts | Not run | Not run | Not run |
| Recorded manual Doc Atlas workflow | Packaged instructions read directly for the trial | Applied manually to TinyRoute | Corrected command, three fixture tests and Markdown preflight recorded |
| Offline release smoke | Starter ZIP extracted and checksum matched | Not applicable | Corrected command printed `Hello, Ada!` and three fixture tests passed |

See the [controlled trial](../plugins/documentation/doc-atlas/evals/workflow-trial.md)
and the [plugin's verification record](../plugins/documentation/doc-atlas/VERIFICATION.md)
for coverage and limits.

Maintainer checks from the repository root.

```sh
python3 scripts/plugin_catalog.py check
python3 -B -m unittest discover -s plugins/documentation/doc-atlas/tests -q
python3 -B -m unittest discover -s plugins/product-and-growth/freelance-legend/tests -q
output=$(mktemp -d)
python3 scripts/pack_starter.py "$output"
(cd "$output" && shasum -a 256 -c SHA256SUMS)
```

The starter builder reads the committed tree. Use `--ref` to select the commit
or tag that the release will identify.
