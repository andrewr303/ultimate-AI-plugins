"""Boundary tests for local site delivery. Browser behavior lives in web.py verify."""
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
import hashlib
import urllib.request
import urllib.error

MODULE = Path(__file__).resolve().parents[1] / 'scripts/web.py'
spec = importlib.util.spec_from_file_location('web', MODULE)
web = importlib.util.module_from_spec(spec)
spec.loader.exec_module(web)


class DeliveryTests(unittest.TestCase):
    def video_package(self, root):
        manifest = {'schemaVersion':'1.0.0','id':'sample-exports','productRevision':'fixture-v1','campaignId':'sample-launch',
                    'variants':[{'id':'sample-landscape','jobPath':'job.json','placement':'landscape','aspectRatio':'16:9',
                    'width':1280,'height':720,'duration':8,'hookId':'proof','bodyId':'workflow','cta':'Try the workflow',
                    'hypothesis':'Visible product action demonstrates the next step.','posterPath':'poster.png',
                    'captionsPath':'captions.srt','outputPath':'video.mp4'}]}
        (root/'export-variants.json').write_text(json.dumps(manifest))
        (root/'job.json').write_text('{}')
        example = MODULE.parents[1] / 'contracts/examples/product-evidence.json'
        evidence = json.loads(example.read_text())
        evidence['product'] = {'name':'Example','revision':'fixture-v1','synthetic':False}
        evidence['claims'] = [{'id':'sample-proof','text':'A bounded sample workflow is implemented.',
                              'status':'verified','sources':[{'type':'repository','path':'job.json','revision':'fixture-v1'}],
                              'allowedUses':['website']}]
        (root/'product-evidence.json').write_text(json.dumps(evidence))
        for name in ('video.mp4','poster.png','captions.srt'):
            (root/name).write_bytes(b'synthetic boundary fixture')
        return manifest

    def test_asset_path_refuses_parent_traversal(self):
        with tempfile.TemporaryDirectory() as root:
            with self.assertRaises(ValueError):
                web.safe_asset(Path(root), '../private.mp4')

    def test_asset_path_refuses_windows_drives_and_separator_aliases(self):
        with tempfile.TemporaryDirectory() as root:
            for path in ['C:/private.mp4', 'media\\video.mp4', './video.mp4', 'media//video.mp4']:
                with self.subTest(path=path), self.assertRaises(ValueError):
                    web.safe_asset(Path(root), path)

    def test_asset_path_refuses_symlink_escape(self):
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as elsewhere:
            external = Path(elsewhere) / 'private.mp4'
            external.write_bytes(b'private')
            try:
                (Path(root) / 'video.mp4').symlink_to(external)
            except OSError:
                self.skipTest('Symlink creation unavailable in this host')
            with self.assertRaises(ValueError):
                web.safe_asset(Path(root), 'video.mp4')

    def test_source_digest_changes_with_content(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            (root / 'index.html').write_text('<h1>First</h1>')
            first = web.source_digest(root)['sha256']
            (root / 'index.html').write_text('<h1>Second</h1>')
            self.assertNotEqual(first, web.source_digest(root)['sha256'])

    def test_serve_refuses_directory_without_index(self):
        with tempfile.TemporaryDirectory() as folder:
            with self.assertRaises(ValueError):
                with web.serve(Path(folder)):
                    pass

    def test_media_server_honors_byte_and_suffix_ranges(self):
        with tempfile.TemporaryDirectory() as folder:
            site = Path(folder)
            (site/'index.html').write_text('<main>Example</main>')
            (site/'video.mp4').write_bytes(b'0123456789')
            with web.serve(site) as url:
                for requested, expected, content_range in [('bytes=2-5',b'2345','bytes 2-5/10'),('bytes=-3',b'789','bytes 7-9/10')]:
                    req = urllib.request.Request(url+'/video.mp4',headers={'Range':requested})
                    with urllib.request.urlopen(req) as result:
                        self.assertEqual(result.status,206)
                        self.assertEqual(result.read(),expected)
                        self.assertEqual(result.headers['Content-Range'],content_range)

    def test_media_server_rejects_unsatisfiable_range(self):
        with tempfile.TemporaryDirectory() as folder:
            site=Path(folder)
            (site/'index.html').write_text('<main>Example</main>')
            (site/'video.mp4').write_bytes(b'0123456789')
            with web.serve(site) as url:
                req=urllib.request.Request(url+'/video.mp4',headers={'Range':'bytes=50-60'})
                with self.assertRaises(urllib.error.HTTPError) as caught:
                    urllib.request.urlopen(req)
                self.assertEqual(caught.exception.code,416)

    def test_video_import_rejects_semantic_ratio_mismatch(self):
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryDirectory() as dest:
            root, site = Path(folder), Path(dest)
            manifest = self.video_package(root)
            manifest['variants'][0]['width'] = 1000
            (root/'export-variants.json').write_text(json.dumps(manifest))
            (site/'workflow.html').write_text('<main></main>')
            with self.assertRaisesRegex(ValueError, 'aspect ratio'):
                web.import_video(site, root)

    def test_video_import_rejects_tampered_declared_hash_before_copy(self):
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryDirectory() as dest:
            root, site = Path(folder), Path(dest)
            self.video_package(root)
            asset = {'id':'source-video','path':'video.mp4','kind':'video','creator':'Example authors','license':'Original example',
                     'source':{'type':'user-supplied','path':'job.json','note':'Synthetic boundary fixture'},'permission':'original',
                     'attribution':'Example','restrictions':[],'sha256':hashlib.sha256((root/'video.mp4').read_bytes()).hexdigest(),
                     'redistributable':True}
            (root/'asset-manifest.json').write_text(json.dumps({'schemaVersion':'1.0.0','id':'sample-rights',
                          'productRevision':'fixture-v1','assets':[asset]}))
            (root/'video.mp4').write_bytes(b'tampered')
            (site/'workflow.html').write_text('<main></main>')
            with self.assertRaisesRegex(ValueError, 'SHA-256 mismatch'):
                web.import_video(site, root)
            self.assertFalse((site/'media').exists())

    def test_video_import_is_generic_and_reports_absent_provenance(self):
        with tempfile.TemporaryDirectory() as folder, tempfile.TemporaryDirectory() as dest:
            root, site = Path(folder), Path(dest)
            self.video_package(root)
            (site/'workflow.html').write_text('<main></main>')
            result = web.import_video(site, root)
            self.assertEqual(result['provenance']['status'],'unverified')
            self.assertNotIn('Tandem',(site/'workflow.html').read_text())
            self.assertNotIn('synthetic sample data',(site/'workflow.html').read_text())
            web.import_video(site, root)
            self.assertEqual((site/'workflow.html').read_text().count('<!-- STUDIO-VIDEO-START -->'),1)


if __name__ == '__main__':
    unittest.main()
