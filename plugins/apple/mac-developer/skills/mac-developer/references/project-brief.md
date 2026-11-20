# Project brief and architecture decision

Copy and fill only applicable fields in the project. Keep facts separate from
assumptions and verify assumptions before depending on them.

- Outcome and observable success:
- Existing products and commands that must continue working:
- Repository state and project instructions:
- Target macOS minimum/current test OS, CPU architectures, Xcode/SDK:
- Existing runtime/dependency versions and current official source checks:
- Chosen UI/runtime and reason; alternatives considered:
- Distribution: development / Developer ID / Mac App Store:
- Processes: UI, worker, browser native host, login helper; owners and lifetimes:
- IPC: endpoints, peer authentication, schema versions, size/rate limits:
- Storage authority, migrations, backups, deletion, optional sync:
- Permissions and why each is needed; behavior when denied:
- Background: login consent, close window, quit, logout, sleep, crash, restart:
- Existing/new compatibility matrix and rollback:
- Implementation slices and evidence for completion:

For companion products, sketch a repository layout such as:

```text
apps/extension/       # existing manifest, permissions, entrypoints remain
apps/mac/             # native target or desktop wrapper
packages/domain/      # platform-independent logic where practical
packages/protocol/    # versioned schemas + compatibility fixtures
services/worker/      # optional bundled runtime, explicit lifecycle
tests/compatibility/  # old/new products + duplicate/offline/restart cases
```

Adapt to existing structure; moving everything into a monorepo is not required.
