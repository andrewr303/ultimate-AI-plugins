# Session Control for Chrome · 0.5.0

A full-tab dashboard for managing Claude Code cloud session links across accounts on your Mac. Click the extension icon to open or focus the dashboard. The warm charcoal, peach accents, workspace tabs, account navigation, and session context follow the visual direction of your supplied screenshot.

## Install on your Mac

1. Unzip this package into a permanent folder. Keep the `extension/` folder there; moving it can change the development extension’s ID.
2. In Google Chrome, open `chrome://extensions`, enable **Developer mode**, and click **Load unpacked**. Select the package’s **extension** folder.
3. Pin **Session Control · Claude Code** to the toolbar. Click it to open the dashboard in a tab. You can also use **⌘⇧Y**; Chrome lets you change shortcuts at `chrome://extensions/shortcuts`.
4. Add an account. Choose **Isolated Chrome profile** for each separate login.
5. Install [Node.js 22 or newer](https://nodejs.org/) if needed. Open `mac-helper/Install Mac Helper.command`, then paste the extension ID shown under the dashboard’s **Settings → Mac helper**. If opening the command file does not launch Terminal, run `bash` followed by a space and drag that file into Terminal, then press Return.
6. Click **Check connection** in Settings. Go to **Accounts → Open account** and sign in to Claude normally. Repeat for your other accounts.
7. Copy a Claude Code session URL from its account window, then click **Save session** in the dashboard. Choose its account and workspace. Opening that saved session routes it to that account’s dedicated Chrome profile.

You do **not** need to run `npm install` to use the extension or helper. They have no runtime npm dependencies. Node is used only by the Mac helper.

## What it does

- Opens a dashboard tab from the toolbar, reusing the existing dashboard tab when possible.
- Maintains account names, optional email labels, and colors.
- Uses a separate persistent Chrome data directory for every isolated account. Google Chrome manages its own login cookies in those directories.
- Organizes session links into workspaces, with search, account/status filters, pins, archives, notes, repository labels, and branch labels.
- Saves your dashboard metadata locally using `chrome.storage.local`.
- Imports and exports JSON metadata backups; logins and cookies are excluded.
- Offers a clearly marked sample workspace that does not overwrite or save into your real workspace.
- Lets you right-click a Claude Code page in the **dashboard’s Chrome profile** to save it. This action can read visible controls once to report a point-in-time page signal. It does not run continuous monitoring.

You may use **This Chrome profile** for one account without installing the helper. It opens links with the login already active in the profile hosting the dashboard. Additional logins require isolated profiles.

## Account isolation and its limits

Multiple regular tabs in one Chrome profile share Claude cookies. An extension cannot assign an independent cookie jar to each tab. Accordingly, **the dashboard lives in a Chrome tab, while isolated account sessions open in their own Chrome windows**. Claude conversations are not embedded or recreated in the dashboard.

Account names and emails are labels you supply. The extension does not verify the signed-in identity. Check the account when you sign in and when saving a session. A session link cannot grant access to a conversation belonging to another account.

Status labels are set by you. Notes, repository, and branch are your own context. The extension does not claim live task progress, usage limits, synchronized transcripts, or automatic discovery of every account’s sessions. It does not submit prompts, auto-approve tools, call private Claude APIs, or automate login.

The extension installed in your main profile is not automatically installed in the isolated account profiles. Copy links from those windows into the central dashboard. Do not install a second dashboard in every account profile unless you intentionally want separate sets of dashboard data.

## Data and helper locations

- Dashboard: local extension storage in the Chrome profile where you installed it. It does not use Chrome Sync.
- Account Chrome profiles: `~/Library/Application Support/SessionControlChrome/Profiles/<profile-id>/`
- Native helper: `~/Library/Application Support/SessionControlChrome/Bridge/`
- Chrome host manifest: `~/Library/Application Support/Google/Chrome/NativeMessagingHosts/com.sessioncontrol.chrome.json`

The helper receives only `ping` and `open` requests from the extension ID you registered. Open requests require an account UUID and an HTTPS URL on `claude.ai/code`. Chrome is launched with an argument array and a small environment allowlist. No cookie reads, credential transfers, localhost web server, or launch-at-login daemon are involved.

Export a metadata backup before removing the extension. Removing an account in the dashboard removes its saved links, while keeping its browser profile and login. Importing a backup replaces the dashboard metadata after confirmation. On the same Mac, retained profile IDs reconnect to the same account folders. On another Mac, you must sign in again.

## Troubleshooting

- **Helper unavailable:** verify Node 22+, Google Chrome, and the exact extension ID. Rerun the installer if the extension folder moved, its ID changed, or Node moved after an upgrade. The helper supports standard Google Chrome, not other Chromium browsers.
- **Wrong account appears:** the saved account label does not verify identity. Check which identity you signed into that account’s dedicated window. Existing Chrome login sessions are not imported into new isolated profiles.
- **Browser verification appears:** complete Claude’s normal verification in the account window. This tool does not bypass it.
- **Session URL rejected:** use a full `https://claude.ai/code/...` address. Ordinary Claude `/chat` and `/c` conversation links are outside this app’s Claude Code scope.
- **Extension shortcut does not work:** assign another shortcut in `chrome://extensions/shortcuts`.
- **Captured link not shown:** finish or close an open editor, then right-click the Claude tab again. Captures are temporary and are not silently saved into an account.

To remove the helper, open `mac-helper/Uninstall Mac Helper.command`. This keeps account profiles and their logins. Uninstalling the extension through Chrome is separate. No running browser is closed by either command.

## Development and verification

Requires Node.js 22+:

```sh
npm ci
npm test
npm run check
```

The automated suite covers dashboard interactions in a simulated DOM, sample-data separation, account validation, session editing and archiving, safe notes rendering, URL restrictions, cross-account routing rejection, native framing, extension-origin binding, installer paths, and intercepted macOS launch arguments. JavaScript/shell syntax and manifest assets are also checked.

**Not verified in this Linux build environment:** real Chrome extension loading or screenshots, macOS `open` behavior, actual Claude login/verification, persistence of those live logins, and signed-in session access. DOM simulation and intercepted launches are supporting tests, not browser or Mac acceptance. See `docs/VALIDATION.md` for local checks.

This is an unpacked development extension with an unsigned local helper, not a Chrome Web Store listing, notarized Mac app, or App Store submission. It is independent of and not affiliated with Anthropic.

## Starting-point source

Based on the uploaded `session-control-native-source-0.4.2.zip`. Its visible-page reader and conservative status adapter are reused under `extension/vendor/`, with module exports adjusted for Manifest V3. The native app’s account-store isolation informed the dedicated Chrome profile approach. The old native/Electron applications, private pairing bridges, historical evidence, and account state are not bundled into this extension. See `docs/PROVENANCE.md`.
