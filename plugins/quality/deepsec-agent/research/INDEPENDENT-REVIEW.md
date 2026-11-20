# Independent DeepSec Agent integration review

Scope: the new `agent-plugin/` runtime, scanner, external adapters, findings/report layer, CLI and host-generation scripts were read independently. The original uploaded app was treated as source material. This is a targeted code review and deterministic validation record, not a certification of security or native host compatibility.

## Findings and disposition

1. **Startup repository root could be redirected between calls.** `runtime/mcp.mjs` originally retained only a canonical pathname and the scanner canonicalized it again per invocation. A root renamed and replaced with a symlink could therefore redirect subsequent scans. Fixed in this review at the parent's request: remember startup directory device/inode; check directory, symlink status, identity and canonical path before tool calls and after scans; reject changes with a fixed error. Regression in `runtime/mcp.test.mjs` renames the root, replaces it with an outside symlink, and verifies a tool error with no outside source location. This reduces pathname substitution risk; it is not a claim of perfect race-free filesystem isolation across platforms.
2. **External snapshot races and deadline gaps.** Initial `runtime/adapters.mjs` used an open that could block if a file became a FIFO, lacked opened-descriptor containment, ignored caller size limits, and only timed external execution after snapshot creation. Sent to adapter owner. Owner added nonblocking opens, inode comparisons, Linux fd containment, bounded looping reads with post-read metadata checks, caller limits and snapshot deadline; inspected the resulting code. External installed tools remain outside an OS sandbox.
3. **Untrusted network option and ignore controls.** Initial external adapter treated arbitrary truthy `allowNetwork` values as opt-in, while project ignore/config files could silently suppress scanner coverage. Owner changed this to strict booleans, excluded source scanner configuration/ignore files, and used trusted packaged configs plus Semgrep `--no-git-ignore`. Network-dependent engines still require explicit selection and opt-in; the adapter is not a network firewall.
4. **Kimi partial results were discarded.** Initial native wrapper treated the CLI's incomplete-coverage exit code as an undifferentiated command failure, discarding findings and coverage. Host owner fixed valid scan-report handling for exits 0/1/2 and added a generated-bundle test with a symlink causing partial coverage. Independently reran host tests successfully.
5. **Portable plugin subtitle exceeded package convention.** Host owner shortened it to `Local security code review`.
6. **CLI and combined-engine details sent to parent.** `--version` branch ordering initially printed help; coverage normalization initially omitted several bounds and omission metadata; combined built-in/external scans could each consume the full requested finding cap; `doctor(root)` initially did not pass that root to executable discovery. Parent owns these corrections and final validation.
7. **Module-stdin scripting edge sent to scanner owner.** A scan launched from `node --input-type=module -` inherited that process flag in a file-based worker and failed. Owner was asked to filter incompatible worker exec arguments and add a subprocess regression. Verify final disposition in the scanner test record.

## Validation executed during this review

- Existing deterministic runtime suite initially passed 33 tests covering scanner boundaries, parser contracts, reports, baselines and bounded execution.
- After the root guard, `node --test runtime/mcp.test.mjs scripts/hosts.test.mjs` passed 8 tests. This includes a real stdio MCP initialize/list/call/scan/review exchange, root-argument rejection, traversal rejection, startup-root replacement, generated host bundles, Kimi partial coverage, no implicit root, and root overrides rejected.
- Test output remained JSON/protocol-safe in the exercised paths. No original uploaded setup program, external scanner installation, live model session, or native Claude/Kimi loader was run by this reviewer.

## Remaining practical limits

- Real Semgrep, Gitleaks, OSV-Scanner, Bandit and Trivy binary behavior is separate from fixture parser/runner contract tests and should be disclosed if not live-tested.
- Claude and Kimi native host loaders were unavailable; generated manifests and wrappers are tested without claiming actual host activation.
- DeepSec regex matches are candidate review locations. File-pattern-only gates and generic candidate severity are explicitly disclosed; these results do not establish vulnerability confirmation or absence.
- Per-file/total/file-count exclusions mean scan completeness is for the declared selected engine and policy, with incomplete states when caps, read errors or skipped special inputs affect coverage.
- Original DeepSec AI/cloud commands remain separate from the bounded plugin. The new runtime does not make the unchanged original CLI's permission behavior equivalent to its own.
