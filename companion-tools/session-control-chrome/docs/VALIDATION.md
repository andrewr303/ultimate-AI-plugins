# Validation · 0.5.0

Automated checks run in Linux with Node 24.19.0. Test results are recorded in `test-results.txt`.

## Supporting checks

- Dashboard interactions tested through jsdom: empty onboarding, sample workspace, editing notes safely, search focus, sample/real storage separation, one-current-profile restriction, separate generated profile IDs, rejected external URLs, saved URL normalization, account-bound session open requests, and archive retrieval.
- Model: backup roundtrip, duplicate IDs and shared profile rejection, broken references and unsupported statuses rejected, conservative unknown status handling.
- Worker: toolbar opens/focuses the full-tab dashboard, native profile routing, cross-account session mismatch refusal, current-profile routing, and sender verification. Chrome APIs are mocked in this test.
- Native host: bounded framed JSON protocol, fragmented/multiple messages, malformed frames, allowed extension origin, profile path containment, no shell interpolation, restrictive launch environment, unsupported platform response, and intercepted macOS launch handoff.
- Installer: writes into a temporary test home, preserves a sentinel profile, quotes unusual paths, and binds only the supplied extension ID. No real user profile, cookie store, or Keychain was accessed.
- Static checks: JavaScript and shell syntax, referenced manifest files, no background host access permissions, and no remote CSS dependencies.

## Mac and Chrome acceptance still to run

These outcomes were **not run** here. The current tool inventory exposes no native interactive browser, and the executor is Linux. A simulated DOM cannot establish visual layout, actual extension permissions, or Mac integration.

| Check | Action on your Mac | Expected outcome |
|---|---|---|
| Full-tab entry | Load unpacked; click the toolbar icon twice | One dashboard tab opens, then is focused again |
| Visual layout | View Sessions, Accounts, Settings at a wide window and a narrow window; try Tab navigation | Readable content, reachable controls, visible focus, no horizontal clipping of core controls |
| Helper | Install with this extension ID, then Check connection | Helper reports connected |
| Two logins | Create two isolated accounts; open each and sign in to different Claude identities | Two separate Chrome profile windows retain their respective identities |
| Persistence | Close those account windows, reopen each through the dashboard | Each profile returns to its own identity, subject to Claude’s normal session expiry |
| Routing | Save a session URL for each account; open each saved link | The matching account profile handles each session |
| First-time/expired login | Open a profile without a live Claude login | Normal Claude sign-in/verification is shown; dashboard does not claim login success |
| Backup | Export; make a temporary label change; import the backup after reviewing confirmation | Saved metadata is restored; logins remain in Chrome |
| Capture | In the dashboard profile, right-click a Claude Code tab and save it | Editor opens; account must be reviewed; no automatic background monitoring |

The helper’s successful response means the OS accepted a Chrome launch request, not that Claude loaded or authenticated. The dashboard wording reflects this distinction.
