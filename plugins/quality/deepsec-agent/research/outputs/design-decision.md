# DeepSec Agent design decision — manual source review

This is a manually supported design report. The optional research bridge and its upstream local checkouts are absent. No automated research verification PASS is claimed. Research informs a real plugin build.

The implementation will preserve the uploaded TypeScript monorepo and reuse its matcher registry in a bounded local Node runtime. Original AI/cloud commands remain available separately. The plugin will use the current host agent for investigation instead of starting a paid background model session.

Security scanners expose structured results suitable for a shared original normalization layer [clm_structured; src_semgrep; src_gitleaks]. Host formats differ and need separate compatibility overlays [clm_hosts; src_codex; src_claude; src_kimi].

| Requirement | Evidence inspected | Gap | Original implementation |
|---|---|---|---|
| Broad source candidates | Uploaded DeepSec packages/scanner/src/matchers/index.ts and matcher-registry.ts | No native local host plugin | Bundle original pure matcher registry; retain attribution |
| Secret engine | gitleaks/gitleaks@8d1f98c7967eb1e79cb44ac6241a124e145d2165:cmd/root.go | Separate report schema | Fixed argv, mandatory full redaction, discard raw secret fields |
| Structural scanner | semgrep/semgrep@087e93b3a1fdf44f97bc92b5b9c2ba221cb2488b:cli/src/semgrep/formatter/json.py | Needs local rules and optional binary | Original JSON adapter, packaged original rules, metrics/version checks disabled |
| Python scanner | PyCQA/bandit:bandit/formatters/json.py (exact SHA in research ledger) | Python only | Optional fixed argv adapter |
| Dependency and infrastructure findings | OSV-Scanner and Trivy pinned evidence being finalized separately | External binaries/databases; no implied offline coverage | Explicit optional adapters and report import; missing tools visible |
| Host installation | OpenAI/Anthropic/Moonshot official docs and pinned implementation (host report) | Different schemas | Portable root, Claude overlay, generated native Kimi wrapper |

No source code from researched external scanners will be copied. Scanner binaries remain separately user-installed tools. Only uploaded DeepSec matchers are redistributed, with the supplied LICENSE and NOTICE retained. This is a conservative packaging decision, not a legal clearance claim.

Acceptance: deterministic vulnerable/safe fixtures; bounded file reads and subprocesses; no raw secrets in reports; explicit incomplete coverage; stable baselines; JSON/Markdown/SARIF exports; MCP initialize/list/call; generated host configurations validated; installation does not write to user settings during development.

## Unresolved

Native Claude and Kimi sessions are not available in this environment. External scanner integration tests depend on installed binaries; fixture parser tests must be distinguished from live-engine validation. Final repository activity/licensing inventory will be included as a separate source-backed report.

## Refuted

No refuted claims are used in this design.
