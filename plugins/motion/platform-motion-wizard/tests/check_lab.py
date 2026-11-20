"""Browser checks for the original local lab using installed Playwright/Chromium.

No browser or dependency installation is performed. These checks exercise this
example, not an application into which it may later be integrated.
"""
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from threading import Thread
import argparse
import json
import shutil
import tempfile

from playwright.sync_api import Error as PlaywrightError, sync_playwright

LAB = Path(__file__).resolve().parents[1] / 'examples' / 'motion-lab'
PROGRESS = "(el) => new DOMMatrixReadOnly(getComputedStyle(el).transform).a"
RUNNING = "(el) => el.getAnimations().some(a => a.playState === 'running')"


class QuietHandler(SimpleHTTPRequestHandler):
    def log_message(self, *args):
        pass


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, help='Evidence directory outside the plugin')
    parser.add_argument('--browser', help='Existing Chromium executable')
    parser.add_argument('--no-sandbox', action='store_true',
                        help='For an isolated container that requires it')
    args = parser.parse_args()
    evidence = args.output.resolve() if args.output else Path(
        tempfile.mkdtemp(prefix='platform-motion-lab-'))
    plugin_root = Path(__file__).resolve().parents[1]
    if evidence == plugin_root or plugin_root in evidence.parents:
        parser.error('Choose an evidence directory outside the plugin')
    evidence.mkdir(parents=True, exist_ok=True)
    executable = args.browser or shutil.which('chromium') or shutil.which('chromium-browser')
    options = {'args': ['--no-sandbox'] if args.no_sandbox else []}
    if executable:
        options['executable_path'] = executable
    server = ThreadingHTTPServer(
        ('127.0.0.1', 0), partial(QuietHandler, directory=str(LAB)))
    Thread(target=server.serve_forever, daemon=True).start()
    checks, script_errors, console_errors, requests = [], [], [], []
    skipped_checks = []
    observations = {}
    failure = None
    browser_version = None

    def observe(page):
        page.on('pageerror', lambda error: script_errors.append(str(error)))
        page.on('console', lambda message: console_errors.append(message.text)
                if message.type == 'error' else None)
        page.on('request', lambda request: requests.append(request.url))

    try:
        with sync_playwright() as runtime:
            browser = runtime.chromium.launch(**options)
            browser_version = browser.version
            page = browser.new_page(viewport={'width': 1140, 'height': 1000},
                                    reduced_motion='no-preference')
            observe(page)
            origin = f'http://127.0.0.1:{server.server_port}'
            page.goto(origin)
            page.wait_for_function("document.documentElement.dataset.reduce === 'false'")

            page.locator('#favorite').click()
            assert page.locator('#favorite').get_attribute('aria-pressed') == 'true'
            page.locator('#favorite').press('Space')
            assert page.locator('#favorite').get_attribute('aria-pressed') == 'false'
            page.locator('#favorite').press('Enter')
            assert page.locator('#favorite').get_attribute('aria-pressed') == 'true'
            checks.append('pointer, Space and Enter change selection immediately')

            page.locator('#openDialog').click()
            assert page.locator('#detail').evaluate('(d) => d.open')
            assert page.locator('#closeDialog').evaluate('(d) => document.activeElement === d')
            page.locator('#replayDialog').click()
            page.wait_for_timeout(40)  # Allow the old queued native close event to dispatch.
            assert page.locator('#detail').evaluate('(d) => d.open')
            assert page.locator('#closeDialog').evaluate('(d) => document.activeElement === d')
            page.keyboard.press('Escape')
            page.wait_for_function("!document.querySelector('#detail').open")
            assert page.locator('#openDialog').evaluate('(d) => document.activeElement === d')
            checks.append('native dialog replay, queued close, Escape and focus return')

            page.locator('#detailDuration').focus()
            page.locator('#detailDuration').press('End')
            page.locator('#toggleDetails').click()
            assert page.locator('#toggleDetails').get_attribute('aria-expanded') == 'true'
            assert not page.locator('#detailsPanel').evaluate('(d) => d.hidden || d.inert')
            assert page.locator('#detailFill').evaluate(RUNNING)
            page.wait_for_function(
                "() => { const v = new DOMMatrixReadOnly(getComputedStyle("
                "document.querySelector('#detailFill')).transform).a; return v > .35 && v < .75; }")
            before_close = page.locator('#detailFill').evaluate(PROGRESS)
            page.locator('#toggleDetails').click()
            assert page.locator('#detailsPanel').evaluate('(d) => d.hidden && d.inert')
            after_close = page.locator('#detailFill').evaluate(PROGRESS)
            assert abs(after_close - before_close) < .25, (before_close, after_close)
            page.locator('#toggleDetails').click()
            after_reopen = page.locator('#detailFill').evaluate(PROGRESS)
            assert abs(after_reopen - after_close) < .25, (after_close, after_reopen)
            assert page.locator('#toggleDetails').get_attribute('aria-expanded') == 'true'
            page.wait_for_function(
                "() => document.querySelector('#detailFill').getAnimations().length === 0")
            assert page.locator('#detailFill').evaluate(PROGRESS) == 1
            assert not page.locator('#detailsPanel').evaluate('(d) => d.hidden || d.inert')
            observations['retarget_progress'] = {
                'before_close': before_close, 'after_close': after_close,
                'after_reopen': after_reopen
            }
            page.locator('#closeDetails').focus()
            page.keyboard.press('Enter')
            assert page.locator('#toggleDetails').evaluate('(d) => document.activeElement === d')
            assert page.locator('#detailsPanel').evaluate('(d) => d.hidden && d.inert')
            checks.append('active open/close/reopen retargets from visible progress; semantics and focus settle immediately')

            # Start a real owned effect, plus an unrelated animation that must survive.
            page.locator('#toggleDetails').click()
            assert page.locator('#detailFill').evaluate(RUNNING)
            page.evaluate("""() => {
                const animation = document.querySelector('#favorite').animate(
                    [{opacity: 1}, {opacity: 1}], {duration: 60000});
                animation.id = 'unrelated-browser-fixture';
            }""")
            page.emulate_media(reduced_motion='reduce')
            page.wait_for_function("document.documentElement.dataset.reduce === 'true'")
            assert page.locator('#detailFill').evaluate('(d) => d.getAnimations().length') == 0
            assert page.locator('#detailFill').evaluate(PROGRESS) == 1
            assert page.locator('#toggleDetails').get_attribute('aria-expanded') == 'true'
            assert not page.locator('#detailsPanel').evaluate('(d) => d.hidden || d.inert')
            assert page.locator('#favorite').evaluate(
                "(d) => d.getAnimations().some(a => a.id === 'unrelated-browser-fixture' && a.playState === 'running')")
            page.locator('#favorite').evaluate(
                "(d) => d.getAnimations().filter(a => a.id === 'unrelated-browser-fixture').forEach(a => a.cancel())")
            page.locator('#reduce').check()
            page.emulate_media(reduced_motion='no-preference')
            page.wait_for_function("document.documentElement.dataset.reduce === 'true'")
            page.locator('#reduce').uncheck()
            page.wait_for_function("document.documentElement.dataset.reduce === 'false'")
            page.emulate_media(reduced_motion='reduce')
            page.locator('#reduce').check()
            page.locator('#reduce').uncheck()
            assert page.locator('html').get_attribute('data-reduce') == 'true'
            page.emulate_media(reduced_motion='no-preference')
            page.wait_for_function("document.documentElement.dataset.reduce === 'false'")
            checks.append('live reduced motion settles owned effect only; system reduction overrides manual setting')

            page.locator('#outcome').select_option('error')
            page.locator('#run').click()  # A
            assert page.locator('#asyncRegion').get_attribute('aria-busy') == 'true'
            page.locator('#outcome').select_option('success')
            page.locator('#run').click()  # B replaces A
            assert page.locator('#queueCount').text_content() == '2'
            page.locator('#deliverLatest').click()  # B arrives first.
            accepted = page.locator('#asyncStatus').text_content()
            assert 'succeeded' in accepted
            assert page.locator('#asyncRegion').get_attribute('aria-busy') == 'false'
            page.locator('#deliverOldest').click()  # A actually arrives.
            assert page.locator('#receivedCount').text_content() == '2'
            assert page.locator('#ignoredCount').text_content() == '1'
            assert page.locator('#asyncStatus').text_content() == accepted

            page.locator('#run').click()
            page.locator('#cancel').click()
            canceled = page.locator('#asyncStatus').text_content()
            assert page.locator('#run').evaluate('(d) => document.activeElement === d')
            assert page.locator('#queueCount').text_content() == '1'
            page.locator('#deliverLatest').click()
            assert page.locator('#receivedCount').text_content() == '3'
            assert page.locator('#ignoredCount').text_content() == '2'
            assert page.locator('#asyncStatus').text_content() == canceled
            assert page.locator('#asyncRegion').get_attribute('aria-busy') == 'false'

            for outcome, text in [('error', 'failed'), ('success', 'succeeded')]:
                page.locator('#outcome').select_option(outcome)
                page.locator('#run').click()
                page.locator('#deliverLatest').click()
                assert text in page.locator('#asyncStatus').text_content()
            checks.append('delivered A after B success and delivered canceled response are ignored; failure/retry remain usable')

            for _ in range(8):
                page.locator('#run').click()
            assert page.locator('#queueCount').text_content() == '8'
            assert page.locator('#run').is_disabled()
            page.locator('#deliverLatest').click()
            assert not page.locator('#run').is_disabled()
            for _ in range(7):
                page.locator('#deliverOldest').click()
            assert page.locator('#queueCount').text_content() == '0'
            assert page.locator('#responseLog li').count() == 6
            assert page.locator('#deliverLatest').is_disabled()
            checks.append('response queue and delivery log stay bounded and recover after delivery')

            page.screenshot(path=str(evidence / 'desktop.png'), full_page=True)
            page.set_viewport_size({'width': 390, 'height': 844})
            page.emulate_media(color_scheme='dark')
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
            page.screenshot(path=str(evidence / 'mobile-dark.png'), full_page=True)
            page.locator('html').evaluate("(d) => d.dir = 'rtl'")
            assert page.evaluate('document.documentElement.scrollWidth <= window.innerWidth')
            page.screenshot(path=str(evidence / 'mobile-dark-rtl.png'), full_page=True)
            checks.append('narrow dark and RTL layouts have no horizontal overflow; stable screenshots captured')

            page.locator('#run').click()
            page.evaluate("window.dispatchEvent(new Event('pagehide'))")
            assert page.locator('#asyncRegion').get_attribute('aria-busy') == 'false'
            assert page.locator('#queueCount').text_content() == '0'
            assert 'leaving' in page.locator('#asyncStatus').text_content()
            page.evaluate("window.dispatchEvent(new Event('pageshow'))")
            page.emulate_media(reduced_motion='reduce')
            page.wait_for_function("document.documentElement.dataset.reduce === 'true'")
            page.locator('#toggleDetails').click()
            assert page.locator('#detailsPanel').evaluate('(d) => d.hidden && d.inert')
            assert page.locator('#detailFill').evaluate(PROGRESS) == 0
            checks.append('synthetic pagehide/pageshow releases fixture work and restores live preference subscription')

            fallback = browser.new_page(reduced_motion='no-preference')
            observe(fallback)
            fallback.add_init_script('Element.prototype.animate = undefined')
            fallback.goto(origin)
            fallback.locator('#toggleDetails').click()
            assert fallback.locator('#toggleDetails').get_attribute('aria-expanded') == 'true'
            assert not fallback.locator('#detailsPanel').evaluate('(d) => d.hidden || d.inert')
            assert fallback.locator('#detailFill').evaluate(PROGRESS) == 1
            fallback.locator('#openDialog').click()
            assert fallback.locator('#detail').evaluate('(d) => d.open')
            assert fallback.locator('#closeDialog').evaluate('(d) => document.activeElement === d')
            fallback.keyboard.press('Escape')
            fallback.close()
            checks.append('missing WAAPI uses stable endpoints with working details, dialog and focus')

            local = browser.new_page(reduced_motion='no-preference')
            observe(local)
            try:
                local.goto((LAB / 'index.html').as_uri())
                local.wait_for_function("document.documentElement.dataset.reduce === 'false'")
                local.locator('#favorite').click()
                assert local.locator('#favorite').get_attribute('aria-pressed') == 'true'
                local.locator('#toggleDetails').click()
                assert local.locator('#toggleDetails').get_attribute('aria-expanded') == 'true'
                local.locator('#run').click()
                local.locator('#deliverLatest').click()
                assert 'succeeded' in local.locator('#asyncStatus').text_content()
                checks.append('direct file:// loading boots classic scripts and usable controls without a server')
            except PlaywrightError as exc:
                if 'net::ERR_BLOCKED_BY_ADMINISTRATOR' not in str(exc):
                    raise
                skipped_checks.append({
                    'check': 'direct file:// loading',
                    'reason': 'Managed Chromium policy blocked local-file navigation (ERR_BLOCKED_BY_ADMINISTRATOR).'
                })
            finally:
                local.close()

            assert not script_errors, script_errors
            assert not console_errors, console_errors
            assert all(url.startswith(origin + '/') or url == origin
                       or url.startswith(LAB.as_uri() + '/') for url in requests), requests
            checks.append('no script errors, console errors or external requests')
            browser.close()
    except Exception as exc:
        failure = f'{type(exc).__name__}: {exc}'
        raise
    finally:
        server.shutdown()
        server.server_close()
        record = {
            'status': 'failed' if failure else 'passed_with_limitations' if skipped_checks else 'passed',
            'browser': 'Chromium via installed Playwright; headless Linux',
            'browser_version': browser_version,
            'checks': checks,
            'skipped_checks': skipped_checks,
            'observations': observations,
            'errors': script_errors + console_errors + ([failure] if failure else []),
            'limitations': [
                'No real mobile hardware, assistive-technology, native-platform or frame-rate validation.',
                'Screenshots establish stable appearance only; retarget checks assess sampled temporal continuity.',
                'Synthetic lifecycle events do not establish actual back-forward cache behavior.',
                'The Windows browser.md reference is unavailable in this Linux workspace; installed Playwright was used.'
            ]
        }
        (evidence / 'results.json').write_text(json.dumps(record, indent=2))
        print(json.dumps({'evidence_directory': str(evidence), **record}, indent=2))


if __name__ == '__main__':
    main()
