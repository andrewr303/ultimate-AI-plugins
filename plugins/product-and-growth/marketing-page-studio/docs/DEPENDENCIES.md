# Dependencies and operating limits

The tested primary environment used Python 3.12.14, Playwright 1.62.0, jsonschema 4.26.0, Pillow 12.3.0, PyYAML 6.0.3, system Chromium and FFmpeg/ffprobe 7.1.5 on Linux. The pinned Python requirements reproduce the tested library versions. Network access is needed to install dependencies; production with supplied local assets uses no paid provider.

Python 3.10+ is the supported code target. Node 20+ is needed only for optional JavaScript renderer projects. `doctor --launch` tests a real browser startup, rather than merely reporting an executable path. Browser and FFmpeg availability are required for the primary video pipeline. Allow several GiB of free space for retained full-resolution frames. Preview first and keep only needed production frames after delivery.

## Windows 11

Use native Python, Playwright Chromium and an installed FFmpeg build on PATH. No primary feature intentionally requires WSL. In PowerShell, open the unpacked plugin directory:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m playwright install chromium
.\.venv\Scripts\python.exe scripts\studio.py doctor --launch
```

Use the virtual environment's Python for subsequent commands. To select a browser for this session: `$env:STUDIO_BROWSER = 'C:\path\to\chrome.exe'`. Windows execution, filesystem edge cases and optional renderer `.cmd` launching have not been tested in this Linux session; run the doctor and example before relying on a Windows delivery. Shell-free Python subprocess argument vectors are used for primary media commands.

## Optional services and renderers

No API credentials are required for the main workflows. The doctor reports presence booleans for optional credentials, never values. Voice, image and music generation are optional extensions chosen for an actual project; no service is called by this plugin by default. Record rights, estimate paid usage and use the host's authorization model before any spend.

HTML/Playwright with FFmpeg is the tested controlled-UI renderer. Real-footage editing is a separate primary adapter. Remotion uses a caller-supplied, installed and licensed project; HyperFrames uses a caller-verified executable and argument vector. Their availability is checked and failure is explicit. Their complete render integrations were not exercised in this session. They never silently substitute another renderer or remove audio.

Fonts use installed system faces unless a project supplies a licensed font. Exact text metrics may differ across hosts; inspect the target host's frames. Browser/FFmpeg dependencies retain their own licenses. Optional Remotion has separate commercial terms.
