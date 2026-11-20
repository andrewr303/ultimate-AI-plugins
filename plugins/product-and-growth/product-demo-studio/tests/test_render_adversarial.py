"""Bounded regressions for renderer file isolation and failed-QA cache safety."""
import contextlib,hashlib,importlib.util,io,json,sys,tempfile,unittest,os
from pathlib import Path
from unittest.mock import patch

PLUGIN=Path(os.environ.get('STUDIO_PLUGIN_ROOT',Path(__file__).resolve().parents[1])).resolve()
sys.path.insert(0,str(PLUGIN/'scripts'))
spec=importlib.util.spec_from_file_location('studio_render',PLUGIN/'scripts'/'render.py')
render=importlib.util.module_from_spec(spec);spec.loader.exec_module(render)

class RenderReview(unittest.TestCase):
 def test_source_does_not_escape_project_by_parent_path(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'project';root.mkdir();(Path(td)/'private.txt').write_text('private')
   with self.assertRaises(ValueError):render.resolve(root,'../private.txt')
 def test_source_does_not_escape_project_by_symlink(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td)/'project';root.mkdir();outside=Path(td)/'outside';outside.mkdir();(outside/'private.txt').write_text('private')
   try:(root/'linked').symlink_to(outside,target_is_directory=True)
   except OSError:self.skipTest('Host cannot create symlinks')
   with self.assertRaises(ValueError):render.resolve(root,'linked/private.txt')
 def test_failed_qa_cache_cannot_return_success(self):
  with tempfile.TemporaryDirectory() as td:
   root=Path(td);job={'schemaVersion':'1.0.0','id':'cache-test','renderer':'html-playwright','productRevision':'r1','visualMode':'illustrative','width':320,'height':180,'fps':12,'duration':1,'hook':'Review me','promise':'A test fixture','cta':'Inspect it','brand':{'name':'Fixture','background':'#ffffff','ink':'#000000','accent':'#333333'},'claimIds':[],'captions':[],'audio':[]}
   jobpath=root/'job.json';jobpath.write_text(json.dumps(job));out=root/'out';out.mkdir();target=out/'video.mp4';target.write_bytes(b'previous rejected encoded file')
   sources=[];fingerprint=hashlib.sha256(json.dumps({'job':job,'sources':sources},sort_keys=True).encode()).hexdigest()
   (out/'render-manifest.json').write_text(json.dumps({'fingerprint':fingerprint,'artifact':{'sha256':render.digest(target)},'qaStatus':'failed'}))
   with patch.object(sys,'argv',['render.py','--job',str(jobpath),'--output',str(out)]),patch.object(render,'validate'),patch.object(render,'source_map',return_value=sources),patch.object(render,'render_html',side_effect=RuntimeError('re-render required')),contextlib.redirect_stdout(io.StringIO()):
    with self.assertRaisesRegex(RuntimeError,'re-render required'):render.main()

if __name__=='__main__':unittest.main(verbosity=2)
