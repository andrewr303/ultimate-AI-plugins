"""Receipt freshness boundary tests use synthetic bytes, not claimed video renders."""
import hashlib,json,os,shutil,subprocess,sys,tempfile,unittest
from pathlib import Path

PLUGIN=Path(os.environ.get('STUDIO_PLUGIN_ROOT',Path(__file__).resolve().parents[1])).resolve()
CHECKER=PLUGIN/'scripts'/'check_receipt.py'
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()

def fixture(root,dependency_hash=None,dependency='ffmpeg'):
 plugin=root/'plugin';(plugin/'scripts').mkdir(parents=True);(plugin/'scripts'/'render.py').write_text('synthetic renderer source fixture');(plugin/'scripts'/'media.py').write_text('synthetic media source fixture')
 project=root/'project';project.mkdir();render=root/'render';render.mkdir();(render/'video.mp4').write_bytes(b'synthetic encoded-byte placeholder; no decode is claimed');job={'id':'synthetic-receipt-unit-test'}
 (render/'job.resolved.json').write_text(json.dumps(job));(render/'qa.json').write_text(json.dumps({'status':'passed','scope':'synthetic checker test only'}));(render/'poster.png').write_bytes(b'synthetic poster placeholder');(render/'captions.srt').write_text('Synthetic test caption')
 version=subprocess.run(['ffmpeg','-version'],capture_output=True,text=True,check=True).stdout.splitlines()[0]
 sources=[{'path':'plugin:scripts/'+n,'sha256':sha(plugin/'scripts'/n)} for n in ['render.py','media.py']]+[{'path':'dependency:'+dependency,'sha256':dependency_hash or hashlib.sha256(version.encode()).hexdigest()}]
 manifest={'schemaVersion':'1.0.0','id':'synthetic-receipt-unit-test','renderer':'html-playwright','productRevision':'synthetic-checker-test-v1','sources':sources,'qaStatus':'passed','artifact':{'path':'video.mp4','sha256':sha(render/'video.mp4')},'assets':[{'path':n,'sha256':sha(render/n)} for n in ['poster.png','captions.srt','qa.json','job.resolved.json']],'fingerprint':hashlib.sha256(json.dumps({'job':job,'sources':sources},sort_keys=True).encode()).hexdigest()}
 (render/'render-manifest.json').write_text(json.dumps(manifest));return plugin,project,render

class ReceiptReview(unittest.TestCase):
 def setUp(self):
  if not shutil.which('ffmpeg'):self.skipTest('ffmpeg required for dependency test')
 def invoke(self,paths):
  plugin,project,render=paths
  result=subprocess.run([sys.executable,str(CHECKER),'--plugin-root',str(plugin),'--project',str(project),'--render',str(render)],capture_output=True,text=True)
  self.assertTrue(result.stdout.strip(),result.stderr)
  return result.returncode,json.loads(result.stdout)
 def test_current_sources_and_dependency_pass(self):
  with tempfile.TemporaryDirectory() as td:
   code,report=self.invoke(fixture(Path(td)))
   self.assertEqual(code,0,report);self.assertTrue(report['passed'],report)
 def test_changed_dependency_cannot_pass(self):
  with tempfile.TemporaryDirectory() as td:
   code,report=self.invoke(fixture(Path(td),'0'*64))
   self.assertNotEqual(code,0);self.assertIn('changed dependency: ffmpeg',report['errors'])
 def test_unverifiable_dependency_cannot_pass(self):
  with tempfile.TemporaryDirectory() as td:
   code,report=self.invoke(fixture(Path(td),'0'*64,'unknown-test-runtime'))
   self.assertNotEqual(code,0);self.assertIn('cannot verify dependency: unknown-test-runtime',report['errors'])
 def test_receipt_without_source_or_configuration_cannot_pass(self):
  with tempfile.TemporaryDirectory() as td:
   paths=fixture(Path(td));render=paths[2];m=json.loads((render/'render-manifest.json').read_text());m.pop('sources');m.pop('assets');m.pop('fingerprint');(render/'render-manifest.json').write_text(json.dumps(m));(render/'qa.json').unlink();(render/'job.resolved.json').unlink()
   code,report=self.invoke(paths)
   self.assertNotEqual(code,0,report);self.assertFalse(report['passed'],report)
 def test_changed_configuration_cannot_pass(self):
  with tempfile.TemporaryDirectory() as td:
   paths=fixture(Path(td));(paths[2]/'job.resolved.json').write_text(json.dumps({'id':'changed-configuration'}));code,report=self.invoke(paths)
   self.assertNotEqual(code,0);self.assertIn('resolved configuration fingerprint differs',report['errors'])
if __name__=='__main__':unittest.main(verbosity=2)
