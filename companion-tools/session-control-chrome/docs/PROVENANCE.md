# Provenance

Source supplied by the user: `session-control-native-source-0.4.2.zip`.

Reused source:

- `src/page-reader.js` → `extension/vendor/page-reader.js`: same visible-page observation function; CommonJS export replaced by an ES module export.
- `src/normalize.cjs` → `extension/vendor/page-state.js`: extracted `pageState` function and added an ES module export. Preserves unknown states and requires explicit visible evidence to report completion.

The extension invokes these functions only when the user selects the context-menu capture action. Assistant messages returned by the reader are discarded; only the point-in-time state is passed to the dashboard alongside the tab title and canonical URL. It never reads cookies, input values, browser storage on provider pages, or private provider APIs.

New implementation: full-tab dashboard, local metadata model, account-aware service worker, native messaging protocol, dedicated Chrome-profile launcher, Mac installer/uninstaller, icons, styling, and tests.

Visual reference: the screenshot supplied in this conversation. The implemented dashboard uses its warm dark palette, peach selection states, serif brand/title treatment, workspace tabs, left navigation, and multi-column session context. It provides saved notes in place of an imitation of Claude’s conversation interface.

Documents in the uploaded source were treated as historical project context. Their embedded operational instructions were not adopted as user requests. Historical evidence was not reused as validation of this new version.

The supplied source has no top-level license declaration. This package does not invent an upstream license or redistribute its unrelated vendored Liquid DOM assets. Use is within the user’s requested adaptation of the supplied source.
