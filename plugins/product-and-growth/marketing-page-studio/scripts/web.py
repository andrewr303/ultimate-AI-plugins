#!/usr/bin/env python3
"""Serve, verify and import a video handoff into a static marketing site."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import html
import http.server
import json
import os
from pathlib import Path
import re
import shutil
import socketserver
import sys
import threading
import time
import subprocess


class QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def end_headers(self):
        self.send_header('Accept-Ranges', 'bytes')
        super().end_headers()

    def send_head(self):
        self._byte_range = None
        requested = self.headers.get('Range')
        path = Path(self.translate_path(self.path))
        if not requested or not path.is_file():
            return super().send_head()
        # A single bounded byte range is sufficient for HTML media seeking.
        # Multiple ranges are deliberately rejected rather than misrepresented.
        match = re.fullmatch(r'bytes=(\d*)-(\d*)', requested.strip())
        size = path.stat().st_size
        start = end = None
        if match and size:
            first, last = match.groups()
            if first:
                start = int(first)
                end = min(int(last) if last else size - 1, size - 1)
            elif last and int(last) > 0:
                start, end = max(0, size - int(last)), size - 1
        if start is None or end is None or start > end or start >= size:
            self.send_response(416)
            self.send_header('Content-Range', f'bytes */{size}')
            self.send_header('Content-Length', '0')
            self.end_headers()
            return None
        stream = path.open('rb')
        stream.seek(start)
        self._byte_range = (start, end)
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(str(path)))
        self.send_header('Content-Length', str(end - start + 1))
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Last-Modified', self.date_time_string(path.stat().st_mtime))
        self.end_headers()
        return stream

    def copyfile(self, source, outputfile):
        selected = getattr(self, '_byte_range', None)
        if selected is None:
            return super().copyfile(source, outputfile)
        remaining = selected[1] - selected[0] + 1
        while remaining:
            data = source.read(min(remaining, 64 * 1024))
            if not data:
                break
            outputfile.write(data)
            remaining -= len(data)


@contextlib.contextmanager
def serve(site: Path):
    if not site.is_dir() or not (site / 'index.html').is_file():
        raise ValueError(f'Site needs an index.html: {site}')
    import functools
    handler = functools.partial(QuietHandler, directory=str(site.resolve()))
    with socketserver.TCPServer(('127.0.0.1', 0), handler) as server:
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            yield f'http://127.0.0.1:{server.server_address[1]}'
        finally:
            server.shutdown()
            thread.join(timeout=2)


def browser_path(explicit=None):
    value = explicit or os.environ.get('STUDIO_BROWSER') or os.environ.get('BROWSER_EXECUTABLE')
    if value:
        if not Path(value).is_file():
            raise ValueError('BROWSER_EXECUTABLE or --browser must name a browser file')
        return value
    for name in ('chromium', 'chromium-browser', 'google-chrome', 'chrome', 'msedge'):
        path = shutil.which(name)
        if path:
            return path
    return None  # Playwright installed-browser resolution is cross-platform.


def safe_asset(root: Path, relative: str):
    if (not isinstance(relative, str) or not relative or '\\' in relative or ':' in relative
            or Path(relative).is_absolute() or any(part in ('', '.', '..') for part in relative.split('/'))):
        raise ValueError(f'Asset needs a safe relative path: {relative}')
    target = (root / relative).resolve()
    if not target.is_relative_to(root.resolve()) or not target.is_file():
        raise ValueError(f'Missing asset or path escapes package: {relative}')
    return target


def import_video(site: Path, package: Path, manifest_name='export-variants.json', variant_id=None):
    """Copy a validated, explicit export; no remote fetch or HTML supplied by package."""
    site, package = site.resolve(), package.resolve()
    if not (site / 'workflow.html').is_file():
        raise ValueError('Video import needs the site workflow.html')
    manifest_path = safe_asset(package, manifest_name)
    manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
    contracts = Path(__file__).resolve().parents[1] / 'contracts'
    schema_path = contracts / 'schemas/export-variants.schema.json'
    if not schema_path.is_file():
        raise ValueError('Bundled contracts/schemas/export-variants.schema.json is missing')
    import jsonschema
    try:
        jsonschema.Draft202012Validator(json.loads(schema_path.read_text(encoding='utf-8'))).validate(manifest)
    except jsonschema.ValidationError as error:
        raise ValueError(f'Invalid export-variants contract at {list(error.absolute_path)}: {error.message}') from error
    evidence_path = package / 'product-evidence.json'

    def validate_contract(name, path, evidence=False):
        command = [sys.executable, str(contracts / 'validate.py'), '--schema', name,
                   '--input', str(path), '--root', str(package), '--check-files']
        if evidence and evidence_path.is_file():
            command += ['--evidence', str(evidence_path), '--use', 'website']
        result = subprocess.run(command, capture_output=True, text=True, timeout=30)
        if result.returncode:
            raise ValueError(f'Invalid {name} handoff: {result.stdout.strip() or result.stderr.strip()}')
        return json.loads(result.stdout)

    validate_contract('export-variants', manifest_path, evidence=True)
    if evidence_path.is_file():
        safe_asset(package, 'product-evidence.json')
        validate_contract('product-evidence', evidence_path)
    variants = manifest['variants']
    if variant_id:
        selected = next((v for v in variants if v['id'] == variant_id), None)
        if selected is None:
            raise ValueError(f'Variant is absent: {variant_id}')
    else:
        selected = next((v for v in variants if v['aspectRatio'] == '16:9'), variants[0])
    source_video = safe_asset(package, selected['outputPath'])
    source_poster = safe_asset(package, selected['posterPath'])
    source_captions = safe_asset(package, selected['captionsPath'])
    if source_video.suffix.lower() not in ('.mp4', '.webm') or source_poster.suffix.lower() not in ('.png', '.jpg', '.jpeg', '.webp'):
        raise ValueError('Import supports local MP4/WebM videos and PNG/JPEG/WebP posters')
    provenance = {'status': 'unverified', 'detail': 'No asset-manifest was supplied; imported byte hashes do not establish source rights or renderer freshness.'}
    rights_path = package / 'asset-manifest.json'
    if rights_path.is_file():
        safe_asset(package, 'asset-manifest.json')
        validate_contract('asset-manifest', rights_path, evidence=True)
        rights = json.loads(rights_path.read_text(encoding='utf-8'))
        if rights['productRevision'] != manifest['productRevision']:
            raise ValueError('Asset manifest and export manifest have different product revisions')
        records = {a['path']: a for a in rights['assets']}
        missing = []
        for key in ('outputPath', 'posterPath', 'captionsPath'):
            record = records.get(selected[key])
            if not record:
                missing.append(selected[key])
            elif record['permission'] == 'unknown' or not record['redistributable']:
                raise ValueError(f'Selected asset has no redistribution permission: {selected[key]}')
        provenance = {'status': 'verified' if not missing else 'partial',
                      'detail': 'Supplied manifest file hashes checked. Renderer source freshness is not re-evaluated by import.',
                      'unregisteredAssets': missing, 'assetManifestSha256': sha256(rights_path)}
    synthetic = False
    if evidence_path.is_file():
        synthetic = json.loads(evidence_path.read_text(encoding='utf-8'))['product'].get('synthetic', False)
    media = site / 'media'
    media.mkdir(exist_ok=True)
    if not media.resolve().is_relative_to(site):
        raise ValueError('Site media directory escapes site')
    paths = {}
    for name, source in [('video', source_video), ('poster', source_poster), ('captions', source_captions)]:
        target = media / ('product-demo-' + name + source.suffix.lower())
        if target.is_symlink():
            raise ValueError('Video import refuses a symlink output')
        shutil.copyfile(source, target)
        paths[name] = target.relative_to(site).as_posix()
    track = f'<track kind="captions" src="{html.escape(paths["captions"])}" srclang="en" label="English" default>' if source_captions.suffix.lower() == '.vtt' else ''
    section = ('<!-- STUDIO-VIDEO-START --><section class="wrap imported-demo" aria-labelledby="video-title">'
               '<p class="eyebrow">SEE THE WORKFLOW</p><h2 id="video-title">A closer look at the product.</h2>'
               f'<p>{"Demonstration using synthetic sample data. " if synthetic else "Product demonstration. "}Play, pause, or explore at your own pace.</p>'
               f'<video controls playsinline preload="metadata" poster="{html.escape(paths["poster"])}" aria-label="Product workflow demonstration">'
               f'<source src="{html.escape(paths["video"])}" type="video/{"mp4" if source_video.suffix.lower()==".mp4" else "webm"}">{track}'
               f'<a href="{html.escape(paths["video"])}">Download the product demonstration</a></video>'
               f'<p><a class="text-link" href="{html.escape(paths["captions"])}">Read the captions ↗</a></p></section><!-- STUDIO-VIDEO-END -->')
    page = site / 'workflow.html'
    text = page.read_text(encoding='utf-8')
    start, end = '<!-- STUDIO-VIDEO-START -->', '<!-- STUDIO-VIDEO-END -->'
    if start in text and end in text:
        text = text[:text.index(start)] + section + text[text.index(end) + len(end):]
    else:
        anchor = next((value for value in ('<section class="wrap queue-section">', '<section class="closing">', '</main>') if value in text), None)
        if not anchor:
            raise ValueError('Video import requires a semantic main closing tag in workflow.html')
        text = text.replace(anchor, section + anchor, 1)
    page.write_text(text, encoding='utf-8')
    report = {'schemaVersion': '1.0.0', 'status': 'passed', 'variantId': selected['id'],
              'productRevision': manifest['productRevision'], 'sourceManifestSha256': sha256(manifest_path),
              'assets': {name: {'path': path, 'sha256': sha256(site / path)} for name, path in paths.items()},
              'provenance': provenance,
              'evidenceStatus': 'validated' if evidence_path.is_file() else 'not-supplied',
              'note': 'Import checks supplied contracts and copies artifact bytes. It does not claim that newer renderer code produced these files. Inspect the encoded video separately.'}
    (media / 'import-report.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    return report


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_digest(site):
    files = {p.relative_to(site).as_posix(): sha256(p) for p in sorted(site.rglob('*')) if p.is_file()}
    digest = hashlib.sha256(json.dumps(files, sort_keys=True).encode()).hexdigest()
    return {'sha256': digest, 'files': files}


def verify(site: Path, output: Path, browser=None):
    from playwright.sync_api import sync_playwright
    output.mkdir(parents=True, exist_ok=True)
    report = {'schemaVersion': '1.0.0', 'suite': 'marketing-browser-acceptance', 'source': source_digest(site),
              'checks': [], 'screenshots': [], 'limitations': ['Automated checks do not establish persuasive design.',
              'Contrast and screen reader announcement quality require independent review.'], 'status': 'running'}
    errors = []

    def check(name, condition, detail=''):
        report['checks'].append({'id': name, 'status': 'passed' if condition else 'failed', 'detail': detail})
        if not condition:
            errors.append(name)

    def screenshot(page, name, full=False):
        target = output / name
        page.screenshot(path=str(target), full_page=full)
        report['screenshots'].append({'path': name, 'sha256': sha256(target), 'width': page.viewport_size['width'],
                                      'workspaceState': page.locator('tandem-workspace').get_attribute('data-state') if page.locator('tandem-workspace').count() else None,
                                      **({'captureContext': 'scroll-story', 'storyState': int(page.locator('[data-story-state]').get_attribute('data-story-state'))} if name.startswith('workflow-scroll-') else {})})

    with serve(site) as url, sync_playwright() as pw:
        executable = browser_path(browser)
        engine = pw.chromium.launch(headless=True, executable_path=executable)
        try:
            for width in (390, 768, 1024, 1440):
                context = engine.new_context(viewport={'width': width, 'height': 900 if width > 560 else 844}, device_scale_factor=1)
                page = context.new_page()
                console_errors = []
                page.on('pageerror', lambda error: console_errors.append(str(error)))
                page.on('console', lambda msg: console_errors.append(msg.text) if msg.type == 'error' else None)
                page.goto(url + '/index.html', wait_until='networkidle')
                page.wait_for_selector('tandem-workspace[data-initialized]')
                page.keyboard.press('Tab')
                check(f'focus-order-skip-{width}', page.locator('.skip-link').evaluate('(el)=>el===document.activeElement'))
                page.keyboard.press('Enter')
                page.wait_for_timeout(120)
                check(f'focus-order-main-{width}', page.evaluate('location.hash === "#main" && document.activeElement.id === "main"'))
                # Focus has been verified. Capture a neutral presentation rather
                # than the keyboard focus outline spanning the full main area.
                page.locator('#hero-title').click()
                page.evaluate('document.activeElement.blur();scrollTo({top:0,behavior:"instant"})')
                box1 = page.locator('#hero-title').evaluate('(el)=>({width:el.offsetWidth,height:el.offsetHeight,x:el.offsetLeft,y:el.offsetTop})')
                page.wait_for_timeout(120)
                box2 = page.locator('#hero-title').evaluate('(el)=>({width:el.offsetWidth,height:el.offsetHeight,x:el.offsetLeft,y:el.offsetTop})')
                check(f'layout-stability-{width}', box1 == box2, 'Headline bounds stable after initial resource settling.')
                overflow = page.evaluate('document.documentElement.scrollWidth > innerWidth')
                check(f'homepage-overflow-{width}', not overflow)
                check(f'semantic-main-{width}', page.locator('main').count() == 1 and page.locator('h1').count() == 1)
                contrast = page.locator('[data-stage="1"] p').evaluate('''el=>{
                  const rgb=s=>s.match(/[\\d.]+/g).slice(0,3).map(Number);
                  const lum=c=>rgb(c).map(v=>{v/=255;return v<=.04045?v/12.92:((v+.055)/1.055)**2.4}).reduce((a,v,i)=>a+v*[.2126,.7152,.0722][i],0);
                  const a=lum(getComputedStyle(el).color),b=lum(getComputedStyle(el.closest('.story-section')).backgroundColor);
                  return (Math.max(a,b)+.05)/(Math.min(a,b)+.05);
                }''')
                check(f'inactive-story-text-contrast-{width}', contrast >= 4.5, f'Computed foreground/background contrast {contrast:.2f}:1; target >=4.5:1.')
                screenshot(page, f'homepage-{width}-initial.png', True)
                page.locator('#triage-button').click()
                check(f'loading-{width}', page.locator('tandem-workspace').get_attribute('data-state') == 'loading')
                check(f'cancel-available-{width}', page.locator('#cancel-demo').is_visible())
                page.wait_for_selector('tandem-workspace[data-state="success"]')
                check(f'billing-route-{width}', page.locator('#route-category').inner_text() == 'Billing' and page.locator('#route-owner').inner_text() == 'Owner: Alex')
                page.locator('#reply-output').fill('Thanks Jamie. I will review the payment details.')
                page.locator('#approve-button').click()
                check(f'editable-review-{width}', page.locator('tandem-workspace').get_attribute('data-review') == 'ready' and 'No message was sent' in page.locator('#workspace-status').inner_text())
                page.locator('.hero-product').scroll_into_view_if_needed()
                screenshot(page, f'homepage-{width}-result.png')
                page.locator('#reset-demo').click()
                check(f'reset-{width}', page.locator('tandem-workspace').get_attribute('data-state') == 'initial' and page.locator('#result-panel').is_hidden())
                page.locator('#sample-select').select_option('empty')
                page.locator('#triage-button').click()
                check(f'empty-{width}', page.locator('tandem-workspace').get_attribute('data-state') == 'empty')
                page.locator('#sample-select').select_option('error')
                page.locator('#triage-button').click()
                page.wait_for_selector('tandem-workspace[data-state="error"]')
                check(f'error-{width}', page.locator('#retry-demo').is_visible())
                if width == 390:
                    screenshot(page, 'homepage-390-error.png')
                page.locator('#retry-demo').click()
                page.wait_for_selector('tandem-workspace[data-state="success"]')
                check(f'retry-{width}', page.locator('#result-panel').is_visible())
                page.locator('#reset-demo').click()
                page.locator('#triage-button').click()
                page.locator('#cancel-demo').click()
                page.wait_for_timeout(950)
                check(f'cancel-does-not-complete-{width}', page.locator('tandem-workspace').get_attribute('data-state') == 'input' and page.locator('#result-panel').is_hidden())
                page.locator('#inbox-search').fill('nothing-matches')
                check(f'filter-empty-{width}', page.locator('.inbox-empty').is_visible())
                page.locator('[data-clear-search]').click()
                check(f'filter-reset-{width}', page.locator('.inbox-count').inner_text() == '3')
                # Direct controls are a usable fallback on touch and reduced-motion.
                page.locator('[data-stage="2"]').click()
                check(f'direct-workflow-{width}', page.locator('[data-story-state]').get_attribute('data-story-state') == '2')
                page.locator('[data-stage="0"]').click()
                check(f'workflow-replay-{width}', page.locator('[data-story-state]').get_attribute('data-story-state') == '0')
                if width == 1440:
                    page.locator('[data-replay-story]').click()
                    page.wait_for_timeout(1250)
                    check('replay-route-stage', page.locator('[data-story-state]').get_attribute('data-story-state') == '1')
                    page.wait_for_timeout(1150)
                    check('replay-review-stage', page.locator('[data-story-state]').get_attribute('data-story-state') == '2')
                    page.locator('[data-replay-story]').click()
                # Real forward/reverse scroll after resetting manual selection.
                if width >= 768:
                    page.mouse.wheel(0, 1)
                    page.wait_for_timeout(40)
                    for index in (0, 1, 2, 1, 0):
                        page.locator(f'[data-stage="{index}"]').evaluate('(el)=>scrollTo({top:el.getBoundingClientRect().top+scrollY+el.offsetHeight/2-innerHeight*.52,behavior:"instant"})')
                        page.wait_for_timeout(90)
                        check(f'scroll-state-{width}-{len(report["checks"])}', page.locator('[data-story-state]').get_attribute('data-story-state') == str(index), f'Reversible state {index}')
                    page.locator('[data-stage="2"]').click()
                    page.wait_for_function('parseFloat(getComputedStyle(document.querySelector(".response-preview")).opacity) >= 0.99')
                    screenshot(page, f'workflow-scroll-{width}-result.png')
                page.locator('#comparison-range').fill('100')
                check(f'comparison-{width}', page.locator('#comparison-value').inner_text() == '100%')
                page.goto(url + '/workflow.html', wait_until='networkidle')
                check(f'feature-overflow-{width}', not page.evaluate('document.documentElement.scrollWidth > innerWidth'))
                page.locator('#tab-intake').focus()
                page.keyboard.press('ArrowRight')
                check(f'tab-keyboard-{width}', page.locator('#tab-route').get_attribute('aria-selected') == 'true' and page.locator('#tab-route').evaluate('(el)=>el===document.activeElement'))
                page.keyboard.press('End')
                check(f'tab-end-{width}', page.locator('#panel-review').is_visible())
                screenshot(page, f'feature-{width}-review.png', True)
                page.locator('[aria-label="Move billing request down"]').click()
                check(f'queue-keyboard-{width}', page.locator('[data-reorder] li').nth(1).get_attribute('data-id') == 'billing')
                page.locator('[data-reset-queue]').click()
                check(f'queue-reset-{width}', page.locator('[data-reorder] li').first.get_attribute('data-id') == 'billing')
                page.goto(url + '/app.html', wait_until='networkidle')
                check(f'app-overflow-{width}', not page.evaluate('document.documentElement.scrollWidth > innerWidth'))
                page.locator('#sample-select').select_option('access')
                page.locator('#triage-button').click()
                page.wait_for_selector('tandem-workspace[data-state="success"]')
                check(f'app-access-workflow-{width}', page.locator('#route-category').inner_text() == 'Account access' and page.locator('#route-owner').inner_text() == 'Owner: Sam')
                if width == 1440:
                    screenshot(page, 'app-1440-access-result.png')
                check(f'console-{width}', not console_errors, '; '.join(console_errors))
                context.close()
            context = engine.new_context(viewport={'width': 390, 'height': 844}, reduced_motion='reduce')
            page = context.new_page()
            page.goto(url + '/index.html', wait_until='networkidle')
            check('reduced-motion-static-story', page.locator('[data-story-state]').get_attribute('data-story-state') == '2' and page.locator('.story-visual').evaluate('(el)=>getComputedStyle(el).position') == 'relative')
            animation_count = page.evaluate('document.getAnimations().filter(a=>a.playState==="running").length')
            check('reduced-motion-no-running-animation', animation_count == 0)
            page.locator('.story-visual').scroll_into_view_if_needed()
            screenshot(page, 'homepage-390-reduced-motion.png')
            page.evaluate('scrollTo(0,document.body.scrollHeight)')
            page.wait_for_timeout(100)
            check('offscreen-observer', page.locator('[data-scroll-story]').get_attribute('data-offscreen') == 'true')
            context.close()
            context = engine.new_context(viewport={'width': 390, 'height': 844}, java_script_enabled=False)
            page = context.new_page()
            page.goto(url + '/index.html', wait_until='networkidle')
            check('no-js-readable-promise', page.locator('#hero-title').is_visible() and 'Every request.' in page.locator('#hero-title').inner_text())
            check('no-js-static-workflow-link', page.locator('noscript a').is_visible())
            context.close()
        finally:
            engine.close()
    report['status'] = 'passed' if not errors else 'failed'
    report['counts'] = {'passed': sum(c['status'] == 'passed' for c in report['checks']), 'failed': len(errors)}
    (output / 'browser-qa.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
    # Contact sheet is a review aid, not an automated visual-design verdict.
    try:
        from PIL import Image, ImageDraw
        names = ['homepage-1440-initial.png', 'homepage-390-initial.png', 'homepage-1440-result.png', 'homepage-390-error.png', 'feature-1440-review.png', 'homepage-390-reduced-motion.png']
        sheet = Image.new('RGB', (1200, 900), '#e8e6df')
        draw = ImageDraw.Draw(sheet)
        for i, name in enumerate(names):
            img = Image.open(output / name).convert('RGB')
            if img.height > img.width * 2:
                img = img.crop((0, 0, img.width, min(img.height, int(img.width * 1.85))))
            img.thumbnail((380, 405))
            x, y = (i % 3) * 400 + 10, (i // 3) * 450 + 30
            draw.text((x, y - 20), name, fill='#18251f')
            sheet.paste(img, (x, y))
        sheet.save(output / 'contact-sheet.jpg', quality=90)
    except ImportError:
        report['limitations'].append('Pillow unavailable; contact sheet omitted.')
    return report


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest='command', required=True)
    verify_parser = sub.add_parser('verify', help='Exercise Tandem fixture interactions and capture responsive browser evidence')
    verify_parser.add_argument('--site', type=Path, required=True)
    verify_parser.add_argument('--output', type=Path, required=True)
    verify_parser.add_argument('--browser')
    serve_parser = sub.add_parser('serve', help='Serve a site on loopback only')
    serve_parser.add_argument('--site', type=Path, required=True)
    serve_parser.add_argument('--port', type=int, default=8080)
    video_parser = sub.add_parser('import-video', help='Consume an export-variants package into the workflow page')
    video_parser.add_argument('--site', type=Path, required=True)
    video_parser.add_argument('--package', type=Path, required=True)
    video_parser.add_argument('--manifest', default='export-variants.json')
    video_parser.add_argument('--variant')
    args = parser.parse_args(argv)
    try:
        if args.command == 'verify':
            report = verify(args.site.resolve(), args.output.resolve(), args.browser)
            print(json.dumps({'status': report['status'], 'counts': report['counts'], 'report': str(args.output / 'browser-qa.json')}))
            return 0 if report['status'] == 'passed' else 1
        if args.command == 'serve':
            import functools
            if not (args.site / 'index.html').is_file():
                raise ValueError('Site requires index.html')
            with socketserver.TCPServer(('127.0.0.1', args.port), functools.partial(QuietHandler, directory=str(args.site.resolve()))) as server:
                print(f'Serving http://127.0.0.1:{args.port}', flush=True)
                server.serve_forever()
        if args.command == 'import-video':
            report = import_video(args.site, args.package, args.manifest, args.variant)
            print(json.dumps(report))
            return 0
    except (ValueError, OSError, ImportError) as error:
        print(json.dumps({'status': 'failed', 'error': str(error), 'remedy': 'Install requirements.txt, then python -m playwright install chromium (or set BROWSER_EXECUTABLE).'}), file=sys.stderr)
        return 2


if __name__ == '__main__':
    raise SystemExit(main())
