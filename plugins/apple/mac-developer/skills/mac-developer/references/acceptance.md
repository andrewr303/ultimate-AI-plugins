# Outcome acceptance

Select cases based on the change. Do not add meaningless tests mirroring code.
Record actual versions, commands, exit status, and remaining manual checks.

| Area | Evidence |
| --- | --- |
| Original form | Original extension/web/CLI build and primary flow still work, app absent and installed |
| Mac integration | Keyboard/menu navigation, multiple windows or menu bar lifecycle, drag/drop/import, VoiceOver and text scaling as applicable |
| Persistence | Relaunch retains data; failure during commit does not corrupt library; migration preserves old data; export/recovery available |
| Background | Window closed, UI quit, explicit stop, login opt-out, logout, sleep/wake, crash, relaunch and uninstall behave as documented |
| Companion capture | Original capture works; screenshot bytes and metadata match; app can organize/search/export received image |
| Reliable transfer | Host missing, app closed, bridge killed mid-transfer, disk full, duplicate ACK/retry, unsupported schema, concurrent browser profiles |
| Security | Disallowed origin/extension ID rejected; malformed/oversize messages rejected; no stdout logging from native host; path traversal and malicious metadata rejected |
| Release | Signed nested executables, selected architecture, clean user install, Gatekeeper/notarization evidence for chosen distribution, upgrade/uninstall tested |

For screenshot transfer, require exactly one library object after retransmission
of the same capture; verify content hash, not just UI count. Interleave two transfers
to expose global-state bugs. Simulate crash after commit before ACK. Test metadata
containing HTML, long text, invalid URLs, unicode, and filenames such as `../x`.
Test permission denial without erasing the outbox. Test captured credentials or
private-page content does not enter logs or an unrequested upload.

A production companion needs independent installation and upgrade paths for the
browser extension and Mac app. Exercise oldest supported protocol versions in
both directions. Mark unsupported combinations clearly instead of dropping data.
