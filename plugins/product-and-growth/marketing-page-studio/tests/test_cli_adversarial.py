import importlib.util,json,tempfile,unittest,argparse,contextlib,io,os
from unittest.mock import patch
from pathlib import Path
from jsonschema import Draft202012Validator

PLUGIN=Path(os.environ.get('STUDIO_PLUGIN_ROOT',Path(__file__).resolve().parents[1])).resolve()
SCRIPT=PLUGIN/'scripts'/'studio.py'
spec=importlib.util.spec_from_file_location('studio',SCRIPT)
studio=importlib.util.module_from_spec(spec);spec.loader.exec_module(studio)
CONTRACTS=PLUGIN/'contracts'

def schema_errors(name,obj):
 schema=json.loads((CONTRACTS/'schemas'/f'{name}.schema.json').read_text())
 return [e.message for e in Draft202012Validator(schema).iter_errors(obj)]

class CLIReview(unittest.TestCase):
 def test_campaign_output_satisfies_contract(self):
  with tempfile.TemporaryDirectory() as td:
   out=Path(td)/'campaign'
   args=argparse.Namespace(brief=str(CONTRACTS/'examples'/'campaign-brief.json'),output=str(out),hooks=3,bodies=2,ratios='9:16,16:9',max_variants=12)
   with contextlib.redirect_stdout(io.StringIO()):studio.campaign(args)
   doc=json.loads((out/'experiment-manifest.json').read_text())
   self.assertEqual(schema_errors('experiment-manifest',doc),[])
 def test_discovery_stays_explicitly_unverified_until_interpreted(self):
  with tempfile.TemporaryDirectory() as td:
   src=Path(td)/'source';src.mkdir();(src/'index.html').write_text('<h1>Fixture</h1>')
   out=Path(td)/'out'
   with contextlib.redirect_stdout(io.StringIO()):studio.discover(argparse.Namespace(source=str(src),output=str(out),allow_network=False))
   self.assertFalse((out/'product-evidence.json').exists())
   doc=json.loads((out/'product-evidence.draft.json').read_text())
   self.assertEqual(doc['claims'],[])
   brief=json.loads((out/'product-brief.json').read_text())
   self.assertIn('not been verified',brief['evidenceStatus'])
 def test_campaign_rejects_invalid_input_before_write(self):
  with tempfile.TemporaryDirectory() as td:
   brief=Path(td)/'brief.json';brief.write_text('{}');out=Path(td)/'campaign'
   args=argparse.Namespace(brief=str(brief),output=str(out),hooks=3,bodies=2,ratios='9:16,16:9',max_variants=12)
   with contextlib.redirect_stdout(io.StringIO()):
    with self.assertRaises(ValueError):studio.campaign(args)
   self.assertFalse(out.exists())
 def test_relative_path_rejects_windows_drive_on_all_hosts(self):
  with tempfile.TemporaryDirectory() as td:
   with self.assertRaises(ValueError):studio.safe_path(td,'C:/private.txt')
 def test_no_parent_traversal(self):
  with tempfile.TemporaryDirectory() as td:
   with self.assertRaises(ValueError):studio.safe_path(td,'../private.txt')
 def test_no_symlink_escape(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'root';root.mkdir();outside=Path(td)/'outside';outside.mkdir();
   try:(root/'link').symlink_to(outside,target_is_directory=True)
   except OSError:self.skipTest('Host cannot create symlinks')
   with self.assertRaises(ValueError):studio.safe_path(root,'link/private.txt')
 def test_invalid_browser_override_is_failure_not_silent_fallback(self):
  with tempfile.TemporaryDirectory() as td:
   out=io.StringIO()
   with patch.dict(os.environ,{'STUDIO_BROWSER':str(Path(td)/'missing-browser')}),contextlib.redirect_stdout(out):
    code=studio.doctor(argparse.Namespace(path=td,launch=False))
   report=json.loads(out.getvalue())
   browser=next(c for c in report['checks'] if c['name']=='browser')
   self.assertNotEqual(code,0)
   self.assertFalse(report['passed'])
   self.assertEqual(browser['status'],'fail')
 def test_campaign_size_cap(self):
  with tempfile.TemporaryDirectory() as td:
   args=argparse.Namespace(brief=str(CONTRACTS/'examples'/'campaign-brief.json'),output=str(Path(td)/'out'),hooks=3,bodies=2,ratios='9:16,16:9,1:1',max_variants=12)
   with self.assertRaises(ValueError):studio.campaign(args)

if __name__=='__main__':unittest.main(verbosity=2)
