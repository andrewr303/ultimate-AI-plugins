"""Exercise a non-Tandem template, actual encoding, bounds, readiness and cache receipts."""
import contextlib
import copy
import io
import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import render

HTML = '''<!doctype html><meta charset="utf-8">
<style>body{margin:0;background:#dbeee8;font:18px Arial;color:#18251f}
[data-pds-role=content]{position:absolute;left:10px;top:10px;width:290px;height:90px}
[data-pds-role=caption]{position:absolute;left:10px;top:110px}
[data-pds-role=cta]{position:absolute;left:10px;top:145px}</style>
<div data-pds-role="content">A separate product</div>
<div data-pds-role="caption">An authored caption</div>
<div data-pds-role="cta">Inspect the result</div>
<script>
window.configure=async config=>{await Promise.resolve();window.config=config;};
window.seek=async time=>{await Promise.resolve();
 document.querySelector('[data-pds-role=content]').textContent=time>=.5?'Result ready':'Preparing';
 return {time,ready:time>=.5};};
</script>'''

def job():
    return dict(schemaVersion='1.0.0', id='custom-fixture', renderer='html-playwright',
                productRevision='fixture-r1', visualMode='illustrative', width=320, height=180,
                fps=12, duration=1, hook='Show the result', promise='A synthetic fixture',
                cta='Inspect', brand=dict(name='Separate fixture', background='#dbeee8',
                ink='#18251f', accent='#224433'), claimIds=[], captions=[dict(start=.2,end=.9,text='Caption')],
                audio=[], template='template.html', reviewPoints=[dict(time=.58,label='settled result')])

def write_evidence(root):
    brief=dict(audience='Test viewers',buyer='Tester',problem='Need a synthetic proof',outcome='Inspect ready state',
               workflow=['Prepare','Inspect'],primaryCapability='Deterministic synthetic state',shipped=['Local fixture'],
               planned=[],conversionAction='Inspect',constraints=['Synthetic'])
    claim=dict(id='synthetic-state',text='A synthetic preparing and ready state.',status='illustrative',
               sources=[dict(type='repository',path='template.html',revision='fixture-r1')],
               allowedUses=['internal','video'],limitations='Test fixture only.')
    evidence=dict(schemaVersion='1.0.0',id='custom-evidence',product=dict(name='Separate fixture',revision='fixture-r1',synthetic=True),claims=[claim],brief=brief)
    (root/'product-evidence.json').write_text(json.dumps(evidence))

class RenderContracts(unittest.TestCase):
    def test_review_points_must_precede_end_and_be_finite(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'template.html').write_text(HTML);write_evidence(root);render.validate(job(),root)
            for value in [1, float('nan'), float('inf')]:
                j=job();j['reviewPoints'][0]['time']=value
                with self.subTest(time=value),self.assertRaises(ValueError):render.validate(j,root)

    def test_layout_targets_use_strict_roles(self):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td);(root/'template.html').write_text(HTML);write_evidence(root);render.validate(job(),root)
            j=job();j['layoutTargets']=[dict(selector='body',role='anything')]
            with self.assertRaisesRegex(ValueError,'Contract validation'):render.validate(j,root)

@unittest.skipUnless(shutil.which('ffmpeg') and shutil.which('ffprobe'),'FFmpeg required')
class CustomTemplateRender(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from playwright.sync_api import sync_playwright
        cls.pw=sync_playwright().start()
        try:cls.browser=cls.pw.chromium.launch(executable_path=render.browser_path(),headless=True,args=['--no-sandbox'])
        except Exception as exc:cls.pw.stop();raise unittest.SkipTest(str(exc))

    @classmethod
    def tearDownClass(cls):cls.browser.close();cls.pw.stop()

    def page(self,html=HTML):
        page=self.browser.new_page(viewport=dict(width=320,height=180))
        page.set_content(html);render.template_call(page,'configure',job())
        return page

    def test_async_seek_and_custom_marker_bounds(self):
        with self.page() as page:
            state=render.template_call(page,'seek',.58)
            self.assertTrue(state['ready'])
            self.assertEqual(page.locator('[data-pds-role=content]').inner_text(),'Result ready')
            targets=render.layout_targets(job(),page)
            records=render.inspect_layout(page,targets,dict(frame=6,time=.5))
            self.assertEqual(len(records),3)
            self.assertTrue(all(x['inside'] for x in records))

    def test_missing_target_clipping_safe_zone_and_hidden_ancestor(self):
        with self.page() as page:
            sample=dict(frame=0,time=0)
            with self.assertRaisesRegex(ValueError,'missing'):
                render.inspect_layout(page,[dict(selector='#absent',role='content')],sample)
            targets=render.layout_targets(job(),page)
            page.locator('[data-pds-role=content]').evaluate('(e)=>e.style.left="100px"')
            with self.assertRaisesRegex(ValueError,'layout review failed'):render.inspect_layout(page,targets,sample)
            page.locator('[data-pds-role=content]').evaluate('(e)=>e.style.display="none"')
            self.assertFalse(render.inspect_layout(page,targets,sample)[0]['visible'])
            with self.assertRaisesRegex(ValueError,'safe zone'):
                render.inspect_layout(page,targets,sample,dict(x=0,y=0,width=320,height=130))

    def test_custom_selectors_and_helpful_missing_contract(self):
        with self.page(HTML.replace('data-pds-role','data-other-role')) as page:
            with self.assertRaisesRegex(ValueError,'requires layoutTargets'):render.layout_targets(job(),page)
            j=job();j['layoutTargets']=[dict(selector='[data-other-role="'+role+'"]',role=role) for role in ['content','cta','caption']]
            self.assertEqual(render.layout_targets(j,page),j['layoutTargets'])

    def test_pending_template_promise_times_out(self):
        with self.page() as page:
            page.evaluate('() => { window.seek=()=>new Promise(()=>{}); }')
            with self.assertRaisesRegex(ValueError,'readiness timed out'):render.template_call(page,'seek',0,100)

    def test_complete_custom_encode_receipt_cache_and_tampered_review(self):
        # Run main through the real command boundary; it owns its Playwright lifecycle.
        self.browser.close();self.pw.stop()
        try:
            with tempfile.TemporaryDirectory() as td:
                root=Path(td);(root/'template.html').write_text(HTML);jp=root/'job.json';jp.write_text(json.dumps(job()));out=root/'render'
                write_evidence(root)
                args=['render.py','--job',str(jp),'--output',str(out)]
                with patch.object(sys,'argv',args),contextlib.redirect_stdout(io.StringIO()):self.assertEqual(render.main(),0)
                manifest=json.loads((out/'render-manifest.json').read_text());qa=json.loads((out/'qa.json').read_text())
                self.assertEqual(qa['status'],'passed')
                frame=next(x for x in qa['reviewFrames'] if 'settled result' in x['labels'])
                self.assertEqual(frame['frame'],6)
                self.assertEqual(frame['time'],.5)
                self.assertIn('review/'+frame['path'],[x['path'] for x in manifest['assets']])
                self.assertTrue(render.receipt_assets_match(out,manifest))
                log=io.StringIO()
                with patch.object(sys,'argv',args),contextlib.redirect_stdout(log):self.assertEqual(render.main(),0)
                self.assertEqual(json.loads(log.getvalue())['status'],'cached')
                (out/'review'/frame['path']).write_bytes(b'tampered review')
                self.assertFalse(render.receipt_assets_match(out,manifest))
                with patch.object(sys,'argv',args),patch.object(render,'render_html',side_effect=ValueError('rerender requested')):
                    with self.assertRaisesRegex(ValueError,'rerender requested'):render.main()
                self.assertEqual(json.loads((out/'render-manifest.json').read_text())['qaStatus'],'incomplete')
        finally:
            from playwright.sync_api import sync_playwright
            self.__class__.pw=sync_playwright().start()
            self.__class__.browser=self.pw.chromium.launch(executable_path=render.browser_path(),headless=True,args=['--no-sandbox'])

if __name__=='__main__':unittest.main(verbosity=2)
