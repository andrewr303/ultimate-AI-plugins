#!/usr/bin/env python3
"""Recheck an encoded artifact and source receipt against current plugin/project files."""
import argparse,hashlib,json,os,re,shutil,subprocess
from pathlib import Path,PurePosixPath

def sha(path):
 h=hashlib.sha256()
 with path.open('rb') as f:
  for part in iter(lambda:f.read(1024*1024),b''):h.update(part)
 return h.hexdigest()
def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--plugin-root',required=True,type=Path);p.add_argument('--project',required=True,type=Path);p.add_argument('--render',required=True,type=Path);p.add_argument('--output',type=Path);a=p.parse_args();errors=[];r=a.render.resolve();m=json.loads((r/'render-manifest.json').read_text());roots={'plugin':a.plugin_root.resolve(),'project':a.project.resolve()}
 for field in ['schemaVersion','id','renderer','productRevision','fingerprint','sources','artifact','assets','qaStatus']:
  if field not in m:errors.append('missing receipt field: '+field)
 if m.get('schemaVersion')!='1.0.0':errors.append('unsupported receipt schema')
 if not isinstance(m.get('fingerprint'),str) or not re.fullmatch('[a-f0-9]{64}',m.get('fingerprint','')):errors.append('missing/invalid resolved configuration fingerprint')
 if not isinstance(m.get('sources'),list) or not m.get('sources'):errors.append('receipt must contain source bindings')
 source_names={s.get('path') for s in m.get('sources',[]) if isinstance(s,dict)}
 if not {'plugin:scripts/render.py','plugin:scripts/media.py'}.issubset(source_names):errors.append('receipt lacks primary renderer implementation bindings')
 asset_names={s.get('path') for s in m.get('assets',[]) if isinstance(s,dict)}
 if not {'poster.png','captions.srt','qa.json','job.resolved.json'}.issubset(asset_names):errors.append('receipt lacks required poster/captions/QA/resolved-job bindings')
 if m.get('artifact',{}).get('path')!='video.mp4':errors.append('receipt artifact must bind video.mp4')
 for entry in m.get('sources',[])+m.get('assets',[])+[m.get('artifact',{})]:
  if not isinstance(entry,dict) or not isinstance(entry.get('sha256'),str) or not re.fullmatch('[a-f0-9]{64}',entry.get('sha256','')):errors.append('invalid receipt file hash')
 for name in ['qa.json','job.resolved.json']:
  if not (r/name).is_file():errors.append('missing required output: '+name)
 def path(root,rel):
  if not rel or '\\' in rel or ':' in rel or PurePosixPath(rel).is_absolute() or '..' in PurePosixPath(rel).parts:raise ValueError('Unsafe receipt path: '+rel)
  target=(root/rel).resolve()
  if not target.is_relative_to(root):raise ValueError('Receipt path escapes root: '+rel)
  return target
 for s in m.get('sources',[]):
  try:
   namespace,rel=s['path'].split(':',1)
   if namespace=='dependency':
    value=None
    if rel in ('ffmpeg','ffprobe'):
     command=shutil.which(rel)
     if command:value=subprocess.run([command,'-version'],capture_output=True,text=True,check=True).stdout.splitlines()[0].encode()
    elif rel=='chromium':
     command=os.environ.get('STUDIO_BROWSER') or next((shutil.which(n) for n in ['chromium','chromium-browser','google-chrome','msedge'] if shutil.which(n)),None)
     if not command:
      try:
       from playwright.sync_api import sync_playwright
       with sync_playwright() as pw:
        candidate=pw.chromium.executable_path
        if Path(candidate).is_file():command=candidate
      except ImportError:pass
     if command:value=subprocess.run([command,'--version'],capture_output=True,text=True,check=True).stdout.strip().encode()
    elif rel.startswith('font-') and shutil.which('fc-match'):
     name=s.get('family') or rel[len('font-'):]
     font=Path(subprocess.run(['fc-match','-f','%{file}',name],capture_output=True,text=True,check=True).stdout.strip())
     if font.is_file():
      if sha(font)!=s['sha256']:errors.append('changed dependency: '+rel)
      continue
    if value is None:errors.append('cannot verify dependency: '+rel)
    elif hashlib.sha256(value).hexdigest()!=s['sha256']:errors.append('changed dependency: '+rel)
    continue
   target=path(roots[namespace],rel)
   if not target.is_file():errors.append('missing source: '+s['path'])
   elif sha(target)!=s['sha256']:errors.append('changed source: '+s['path'])
  except (KeyError,ValueError,OSError,subprocess.SubprocessError) as e:errors.append(str(e))
 for entry in [m.get('artifact',{})]+m.get('assets',[]):
  try:
   target=path(r,entry['path'])
   if not target.is_file():errors.append('missing output: '+entry['path'])
   elif sha(target)!=entry['sha256']:errors.append('changed output: '+entry['path'])
  except (KeyError,ValueError,OSError,subprocess.SubprocessError) as e:errors.append(str(e))
 if m.get('qaStatus')!='passed':errors.append('technical QA is not passed')
 q=r/'qa.json'
 if q.is_file() and json.loads(q.read_text()).get('status')!='passed':errors.append('QA report status is not passed')
 resolved=r/'job.resolved.json'
 if resolved.is_file():
  expected=hashlib.sha256(json.dumps({'job':json.loads(resolved.read_text()),'sources':m.get('sources',[])},sort_keys=True).encode()).hexdigest()
  if expected!=m.get('fingerprint'):errors.append('resolved configuration fingerprint differs')
 result={'passed':not errors,'render':str(r),'manifestSha256':sha(r/'render-manifest.json'),'errors':errors,'scope':'Source/dependency/output/configuration freshness only; no new creative review or render.'};text=json.dumps(result,indent=2)
 if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text+'\n')
 print(text);return 1 if errors else 0
if __name__=='__main__':raise SystemExit(main())
