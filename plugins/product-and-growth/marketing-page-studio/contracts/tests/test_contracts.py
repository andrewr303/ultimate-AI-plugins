import copy
import importlib.util
import json
import hashlib
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('contracts_validate',ROOT/'validate.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

def example(name):return json.loads((ROOT/'examples'/f'{name}.json').read_text())

class ProductionContracts(unittest.TestCase):
    def test_all_examples(self):
        for path in (ROOT/'examples').glob('*.json'):
            with self.subTest(schema=path.stem):
                report=module.validate(path.stem,json.loads(path.read_text()))
                self.assertTrue(report['ok'],report)
    def assert_invalid(self,name,data,code=None,**kwargs):
        report=module.validate(name,data,**kwargs)
        self.assertFalse(report['ok'],report)
        if code:self.assertIn(code,[e['code'] for e in report['errors']],report)
    def test_no_path_traversal(self):
        for unsafe in ['/tmp/capture.png','../private.png','captures/../../private.png','C:/private.png','captures\\private.png']:
            data=example('capture-manifest');data['assets'][0]['path']=unsafe
            with self.subTest(unsafe=unsafe):self.assert_invalid('capture-manifest',data,'path')
    def test_capture_hold_is_bounded(self):
        data=example('capture-job');data['steps'][1]['holdMs']=10001
        self.assert_invalid('capture-job',data,'schema')
    def test_capture_hold_requires_ready_state(self):
        data=example('capture-job');data['steps'][0]['holdMs']=1000
        self.assert_invalid('capture-job',data)
    def test_verified_claim_needs_support(self):
        data=example('product-evidence');data['claims'][0]['sources']=[]
        self.assert_invalid('product-evidence',data,'evidence')
    def test_provenance_needs_location(self):
        data=example('product-evidence');data['claims'][0]['sources']=[{'type':'capture','revision':data['product']['revision']}]
        self.assert_invalid('product-evidence',data)
    def test_unsupported_claim_never_published(self):
        data=example('product-evidence');data['claims'][1]['allowedUses']=['ads']
        self.assert_invalid('product-evidence',data,'evidence')
    def test_missing_local_product_evidence_source(self):
        evidence=example('product-evidence')
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            self.assertTrue(module.validate('product-evidence',evidence,project_root=root)['ok'])
            self.assert_invalid('product-evidence',evidence,'file',project_root=root,check_files=True)
            (root/'product').mkdir();(root/'product/index.html').write_text('Synthetic fixture source')
            self.assertTrue(module.validate('product-evidence',evidence,project_root=root,check_files=True)['ok'])
    def test_contextual_evidence_propagates_file_checks(self):
        evidence=example('product-evidence');campaign=example('campaign-brief')
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'product-evidence.json').write_text(json.dumps(evidence));(root/'brand.json').write_text(json.dumps(example('brand')))
            report=module.validate('campaign-brief',campaign,project_root=root,check_files=True,use='ads')
            self.assertFalse(report['ok'],report)
            self.assertTrue(any('Missing local evidence source' in e['message'] for e in report['errors']),report)
            (root/'product').mkdir();(root/'product/index.html').write_text('Synthetic fixture source')
            self.assertTrue(module.validate('campaign-brief',campaign,project_root=root,check_files=True,use='ads')['ok'])
    def test_revision_mismatch(self):
        data=example('product-evidence');data['claims'][0]['sources'][0]['revision']='obsolete-v0'
        self.assert_invalid('product-evidence',data,'evidence')
    def test_capture_rights_manifest_linkage(self):
        capture=example('capture-manifest');rights=example('asset-manifest')
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);path=root/'asset-manifest.json';path.write_text(json.dumps(rights))
            self.assertTrue(module.validate('capture-manifest',capture,project_root=root)['ok'])
            capture['assets'][0]['rightsId']='wrong-document'
            self.assert_invalid('capture-manifest',capture,'rights',project_root=root)
            capture['assets'][0]['rightsId']=rights['id'];rights['assets'][0]['sha256']='a'*64;path.write_text(json.dumps(rights))
            self.assert_invalid('capture-manifest',capture,'rights',project_root=root)
    def test_duplicate_ids(self):
        data=example('capture-manifest');data['assets'].append(copy.deepcopy(data['assets'][0]))
        self.assert_invalid('capture-manifest',data,'duplicate-id')
    def test_unreachable_interactive_state(self):
        data=example('interactive-demo');data['states'].append({'id':'invisible','label':'Invisible','purpose':'Never reachable'})
        self.assert_invalid('interactive-demo',data)
    def test_caption_outside_safe_zone(self):
        data=example('storyboard');data['shots'][0]['captionBounds']={'x':0,'y':0,'width':100,'height':100}
        self.assert_invalid('storyboard',data)
    def test_shot_overlaps(self):
        data=example('storyboard');data['shots'][1]['startFrame']=30
        self.assert_invalid('storyboard',data)
    def test_incorrect_export_ratio(self):
        data=example('export-variants');data['variants'][0]['width']=1080
        self.assert_invalid('export-variants',data)
    def test_render_caption_bounds(self):
        data=example('render-job');data['captions'][0]['end']=100
        self.assert_invalid('render-job',data)
    def test_render_evidence_and_font_paths_stay_relative(self):
        for key in ('evidence','font'):
            for unsafe in ('../private.json','C:/private.json'):
                data=example('render-job');data[key]=unsafe
                with self.subTest(key=key,path=unsafe):self.assert_invalid('render-job',data,'path')
    def test_render_safe_zone_fits_composition(self):
        data=example('render-job');data['safeZone']={'x':9999,'y':0,'width':10,'height':10}
        self.assert_invalid('render-job',data)
    def test_non_web_url_is_not_product_evidence(self):
        data=example('product-evidence');data['claims'][0]['sources']=[{'type':'website','url':'file:///private'}]
        self.assert_invalid('product-evidence',data,'url')
    def test_internal_planning_can_reference_published_claim(self):
        report=module.validate('campaign-brief',example('campaign-brief'),evidence=example('product-evidence'),use='internal')
        self.assertTrue(report['ok'],report)
    def test_optional_config_hash_binds_configuration(self):
        data=example('render-job');data['configHash']='0'*64
        self.assert_invalid('render-job',data,'hash')
        payload={k:v for k,v in data.items() if k!='configHash'}
        data['configHash']=hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(',',':'),ensure_ascii=False).encode()).hexdigest()
        self.assertTrue(module.validate('render-job',data)['ok'])
    def test_footage_requires_source(self):
        data=example('render-job');data['renderer']='footage'
        self.assert_invalid('render-job',data)
    def test_duplicate_hooks_not_experiments(self):
        data=example('experiment-manifest');data['hooks'][1]['text']=data['hooks'][0]['text']
        self.assert_invalid('experiment-manifest',data)
    def test_unknown_rights_cannot_be_redistributed(self):
        data=example('asset-manifest');data['assets'][0]['permission']='unknown'
        self.assert_invalid('asset-manifest',data,'rights')
    def test_pass_needs_actual_evidence(self):
        data=example('qa-results');data['checks'][0]['status']='pass'
        self.assert_invalid('qa-results',data,'evidence')
    def test_source_binding_rejects_changed_file(self):
        data=example('qa-results')
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);(root/'storyboard.json').write_text('actual source')
            self.assert_invalid('qa-results',data,'hash',project_root=root)
            data['sourceHashes']['storyboard.json']=hashlib.sha256((root/'storyboard.json').read_bytes()).hexdigest()
            self.assertTrue(module.validate('qa-results',data,project_root=root)['ok'])
    def test_symlink_cannot_escape_root(self):
        with tempfile.TemporaryDirectory() as inside,tempfile.TemporaryDirectory() as outside:
            root=Path(inside);external=Path(outside)/'private';external.write_text('private')
            try:(root/'storyboard.json').symlink_to(external)
            except OSError:self.skipTest('Host cannot create symlinks')
            data=example('qa-results')
            self.assert_invalid('qa-results',data,'path',project_root=root)
    def test_contextual_claim_allowlist(self):
        data=example('campaign-brief');data['claims']=['automatic-integrations']
        self.assert_invalid('campaign-brief',data,'evidence',evidence=example('product-evidence'),use='ads')
    def test_missing_contextual_evidence(self):
        with tempfile.TemporaryDirectory() as folder:
            self.assert_invalid('campaign-brief',example('campaign-brief'),'evidence',project_root=Path(folder))

if __name__=='__main__':unittest.main()
