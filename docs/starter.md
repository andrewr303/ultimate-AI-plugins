# Doc Atlas starter

The starter contains Doc Atlas 1.0.1 and the TinyRoute fixture used in the
[worked example](../README.md#see-doc-atlas-in-action).

Download `doc-atlas-starter-v1.0.1.zip` and `SHA256SUMS` from
[Doc Atlas Starter 1.0.1](https://github.com/andrewr303/ultimate-AI-plugins/releases/tag/doc-atlas-starter-v1.0.1).
From the directory that contains both downloads, verify and extract the package.

```sh
shasum -a 256 -c SHA256SUMS
unzip doc-atlas-starter-v1.0.1.zip
cd doc-atlas-starter
```

Use the instructions for your [host](hosts.md). From the extracted starter root,
Codex can register the included one-plugin marketplace and Claude Code can
load the plugin from its directory.

```sh
codex plugin marketplace add "$PWD"
codex plugin add doc-atlas@ultimate-ai-plugins-starter
```

```sh
claude --plugin-dir ./plugins/documentation/doc-atlas
```

For Kimi Code, use `/plugins install` with the absolute path to the extracted
`plugins/documentation/doc-atlas` directory, then run `/reload`.

To run the example without an agent or account, use Python 3.10 or later from
the extracted starter root.

```sh
cd plugins/documentation/doc-atlas/evals/fixtures/tinyroute
PYTHONPATH=src python3 -m tinyroute --name Ada
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

The CLI prints `Hello, Ada!`, and the three fixture tests pass. See
[host verification](verification.md) for observed coverage and
[legacy archives](../artifacts/README.md) for earlier packages.
