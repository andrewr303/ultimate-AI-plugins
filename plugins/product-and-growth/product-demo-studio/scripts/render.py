#!/usr/bin/env python3
"""Offline deterministic frame renderer and real-footage editor. No paid services or silent fallback."""
from __future__ import annotations
import argparse,copy,hashlib,importlib.util,json,math,os,re,shutil,subprocess,sys,tempfile,time
from pathlib import Path
from media import digest,probe,inspect,run,review_samples
ROOT=Path(__file__).resolve().parents[1]

def resolve(base,value):
 if not isinstance(value,str) or not value or "\\" in value or ":" in value or Path(value).is_absolute() or '..' in Path(value).parts:
  raise ValueError(f'Asset path must be a traversal-free relative project path: {value}')
 base=Path(base).resolve();p=(base/value).resolve()
 if not p.is_relative_to(base):raise ValueError(f'Asset escapes project root: {value}')
 if not p.is_file():raise ValueError(f'Asset missing: {value}')
 return p

def validate(job,base):
 for key in ['id','renderer','productRevision','visualMode','width','height','fps','duration','hook','promise','cta','brand']:
  if key not in job:raise ValueError(f'Missing field: {key}')
 if job['renderer'] not in ['html-playwright','footage','remotion','hyperframes']:raise ValueError('Unknown renderer')
 if job['visualMode'] not in ['faithful-replay','recorded','illustrative']:raise ValueError('Unknown visualMode')
 for k in ['width','height']:
  if not isinstance(job[k],int) or job[k]<160 or job[k]>4096 or job[k]%2:raise ValueError(f'{k} must be an even integer 160..4096')
 if not isinstance(job['fps'],(int,float)) or job['fps'] not in [12,15,24,25,30,60]:raise ValueError('fps must be 12,15,24,25,30 or 60')
 if not isinstance(job['duration'],(int,float)) or not 1<=job['duration']<=180:raise ValueError('duration must be 1..180 seconds')
 if abs(round(job['duration']*job['fps'])-job['duration']*job['fps'])>.0001:raise ValueError('duration must resolve to whole frames')
 for k in ['name','background','ink','accent']:
  if not job['brand'].get(k):raise ValueError(f'brand.{k} missing')
 if any(len(str(job[k]))>150 for k in ['hook','promise','cta']):raise ValueError('Text exceeds concise composition limits; author a custom template instead')
 previous=0
 for c in job.get('captions',[]):
  if not 0<=c['start']<c['end']<=job['duration'] or c['start']<previous:raise ValueError('Captions must be nonoverlapping, sorted, and inside duration')
  if len(c['text'])>110:raise ValueError('Caption too long; split at a thought boundary')
  previous=c['end']
 for a in job.get('audio',[]):
  resolve(base,a['path'])
  if a.get('role') not in ['narration','music','sfx']:raise ValueError('Audio role missing or invalid')
  if not a.get('rightsId'):raise ValueError('Audio asset requires rightsId')
  if a.get('start',0)<0 or a.get('start',0)>=job['duration']:raise ValueError('Audio start outside video')
  if not -60<=a.get('gainDb',0)<=12:raise ValueError('Audio gain outside supported range')
 if job.get('claimIds'):
  if not job.get('evidence'):raise ValueError('claimIds require evidence manifest')
  evidence=json.loads(resolve(base,job['evidence']).read_text());claims={c['id']:c for c in evidence.get('claims',[])}
  if evidence.get('product',{}).get('revision')!=job['productRevision']:raise ValueError('Evidence product.revision differs from render job')
  for cid in job['claimIds']:
   if cid not in claims or claims[cid].get('status') not in ['verified','supplied','illustrative'] or 'video' not in claims[cid].get('allowedUses',[]):raise ValueError(f'Claim {cid} has no usable video evidence')
 if job.get('audio') and job.get('source',{}).get('audioPolicy')=='preserve':raise ValueError('Preserved source audio with external tracks is not supported; prepare an explicitly mixed master first. Source audio will not be silently dropped.')
 for rel,expected in job.get('sourceHashes',{}).items():
  if digest(resolve(base,rel))!=expected:raise ValueError('Source hash mismatch: '+rel)
 validator=ROOT/'contracts'/'validate.py'
 if validator.is_file():
  spec=importlib.util.spec_from_file_location('studio_contracts',validator);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  result=module.validate('render-job',job,project_root=Path(base),evidence=evidence if job.get('claimIds') else None,use='video',check_files=True)
  if not result['ok']:raise ValueError('Contract validation failed: '+json.dumps(result))
 if job['renderer']=='html-playwright' and not job.get('template'):
  fixture=json.loads((ROOT/'examples/tandem/product-evidence.json').read_text())
  if job['brand']['name']!='Tandem' or job['productRevision']!=fixture['product']['revision']:
   raise ValueError('The built-in Tandem template is only for the bundled synthetic fixture. Supply an explicit self-contained template using verified components/states for this product; brand tokens alone do not replace the interface.')
 if job['renderer']=='footage':
  if job['visualMode']!='recorded':raise ValueError('Footage adapter requires recorded visualMode')
  source=resolve(base,job.get('source',{}).get('path',''));data=probe(source);stream=next(s for s in data['streams'] if s['codec_type']=='video');d=float(data['format']['duration'])
  if job['source'].get('start',0)+job['duration']>d+.05:raise ValueError('Source ends before requested cut; trim duration explicitly')
  if any(s['codec_type']=='audio' for s in data['streams']) and job['source'].get('audioPolicy') not in ['preserve','mute']:raise ValueError('Source contains audio; set audioPolicy preserve or mute explicitly')
  if job['source'].get('audioPolicy')=='preserve' and not any(s['codec_type']=='audio' for s in data['streams']):raise ValueError('Source has no audio to preserve; set audioPolicy mute explicitly')
  crop=job['source'].get('crop')
  if crop and (len(crop)!=4 or min(crop)<0 or crop[2]<=0 or crop[3]<=0 or crop[0]+crop[2]>stream['width'] or crop[1]+crop[3]>stream['height']):raise ValueError('Source crop outside source pixels')


def browser_path():
 if os.environ.get('STUDIO_BROWSER'):
  if not Path(os.environ['STUDIO_BROWSER']).is_file():raise ValueError('STUDIO_BROWSER does not exist')
  return os.environ['STUDIO_BROWSER']
 for name in ['chromium','chromium-browser','google-chrome','msedge']:
  found=shutil.which(name)
  if found:return found
 return None

def source_map(job,job_path):
 paths=[Path(__file__),Path(__file__).with_name('media.py'),job_path,ROOT/'examples/tandem/composition.html'];base=job_path.parent
 paths += [p for p in [ROOT/'contracts/validate.py',ROOT/'contracts/schemas/render-job.schema.json',ROOT/'contracts/schemas/product-evidence.schema.json'] if p.is_file()]
 for rel in job.get('sourceHashes',{}):paths.append(resolve(base,rel))
 for value in [job.get('template'),job.get('evidence'),job.get('font'),job.get('source',{}).get('path')]+[a['path'] for a in job.get('audio',[])]:
  if value:paths.append(resolve(base,value))
 if not job.get('evidence') and (base/'product-evidence.json').is_file():paths.append(resolve(base,'product-evidence.json'))
 records=[{'path':('plugin:'+p.relative_to(ROOT).as_posix()) if p.is_relative_to(ROOT) else ('project:'+p.relative_to(base).as_posix()),'sha256':digest(p)} for p in dict.fromkeys(paths)]
 for tool in ['ffmpeg','ffprobe']:
  version=run([tool,'-version']).stdout.splitlines()[0];records.append({'path':'dependency:'+tool,'sha256':hashlib.sha256(version.encode()).hexdigest(),'version':version})
 if job['renderer']=='html-playwright' and browser_path():
  version=run([browser_path(),'--version']).stdout.strip();records.append({'path':'dependency:chromium','sha256':hashlib.sha256(version.encode()).hexdigest(),'version':version})
 if shutil.which('fc-match'):
  for family in ['Arial','Georgia']:
   font=Path(run(['fc-match','-f','%{file}',family]).stdout.strip())
   if font.is_file():records.append({'path':'dependency:font-'+family,'sha256':digest(font),'family':family,'resolvedFont':font.name})
 return records

def validate_template(html):
 from html.parser import HTMLParser
 class Resources(HTMLParser):
  def handle_starttag(self,tag,attrs):
   a=dict(attrs)
   for attr in (['href'] if tag in ['link','use'] else ['data'] if tag=='object' else ['src','srcset'] if tag in ['img','video','audio','source','script','iframe','embed','track','input'] else []):
    value=a.get(attr,'').strip()
    if value and not value.startswith(('data:','#')):raise ValueError(f'Template must be self-contained; inline {tag}.{attr} resource as a data URI: {value}')
 Resources().feed(html)
 if re.search(r'@import\s',html,re.I):raise ValueError('Template CSS @import is unsupported; inline its content before rendering')
 for value in re.findall(r'url\(\s*([^)]*)\)',html,re.I):
  value=value.strip().strip('"\'')
  if value and not value.startswith(('data:','#')):raise ValueError('Template CSS resource must be an inline data URI: '+value)

def template_call(page,method,value,timeout_ms=15000):
 """Await the template-owned state and its fonts/images before sampling pixels."""
 from playwright.sync_api import Error as BrowserError
 try:return page.evaluate("""async ({method,value,timeout}) => {
  let timer;
  const ready = async () => {
   if (typeof window[method] !== 'function') throw new Error('Template must expose window.'+method+'()');
   const state = await window[method](value);
   await document.fonts.ready;
   await Promise.all([...document.images].map(image => image.decode()));
   return state;
  };
  try { return await Promise.race([ready(), new Promise((_,reject) => {
   timer = setTimeout(() => reject(new Error('Template '+method+' readiness timed out')), timeout);
  })]); } finally { clearTimeout(timer); }
 }""",{'method':method,'value':value,'timeout':timeout_ms})
 except BrowserError as exc:raise ValueError(f'Template {method} failed: {str(exc)[:1500]}') from exc

def layout_targets(job,page):
 defaults=[{'selector':'#'+id,'role':'caption' if id=='caption' else 'cta' if id=='cta' else 'content',**({'container':'#app-wrap'} if id in ['approve','reply'] else {})} for id in ['headline','app-wrap','proof','cta','caption','mode','end-note','approve','reply']]
 if not job.get('template'):return defaults
 targets=job.get('layoutTargets')
 if targets is None:
  roles=page.locator('[data-pds-role]').evaluate_all('(elements)=>[...new Set(elements.map(e=>e.dataset.pdsRole))]')
  if roles:
   if any(role not in ['content','caption','cta'] for role in roles):raise ValueError('data-pds-role must be content, caption or cta')
   targets=[{'selector':'[data-pds-role="'+role+'"]','role':role} for role in roles]
  elif all(page.locator(t['selector']).count() for t in defaults):return defaults
  else:raise ValueError('Custom template requires layoutTargets or data-pds-role markers for content, cta and authored captions')
 required={'content','cta'}|({'caption'} if job.get('captions') else set())
 if not required.issubset({t['role'] for t in targets}):raise ValueError('Custom layoutTargets must cover content, cta and authored captions')
 return targets

def inspect_layout(page,targets,sample,safe_zone=None):
 records=page.evaluate("""targets => targets.flatMap(target => {
  const elements=[...document.querySelectorAll(target.selector)];
  if(!elements.length) return [{...target,missing:true,visible:false,inside:false}];
  return elements.map(e => {
   const r=e.getBoundingClientRect(); let visible=!!e.getClientRects().length;
   for(let parent=e;parent;parent=parent.parentElement) {
    const style=getComputedStyle(parent);
    if(style.display==='none'||['hidden','collapse'].includes(style.visibility)||Number(style.opacity)<=.05) visible=false;
   }
   const container=target.container ? document.querySelector(target.container).getBoundingClientRect() : null;
   const inside=r.left>=0&&r.top>=0&&r.right<=innerWidth+1&&r.bottom<=innerHeight+1&&(!container||r.left>=container.left&&r.top>=container.top&&r.right<=container.right&&r.bottom<=container.bottom-2);
   const style=getComputedStyle(e);
   return {...target,visible,inside,rect:[r.x,r.y,r.width,r.height],scrollWidth:e.scrollWidth,clientWidth:e.clientWidth,
    clippedY:['hidden','clip'].includes(style.overflowY)&&e.scrollHeight>e.clientHeight+1};
  });
 })""",targets)
 for record in records:
  record.update(time=sample['time'],frame=sample['frame'])
  if safe_zone and record['visible'] and record['role'] in ['caption','cta']:
   x,y,w,h=record['rect'];z=safe_zone
   record['insideSafeZone']=x>=z['x'] and y>=z['y'] and x+w<=z['x']+z['width']+1 and y+h<=z['y']+z['height']+1
 failures=[r for r in records if r.get('missing') or (r['visible'] and (not r['inside'] or r['scrollWidth']>r['clientWidth']+1 or r['clippedY'] or not r.get('insideSafeZone',True)))]
 if failures:raise ValueError('Composition layout review failed (missing, clipped or outside frame/safe zone): '+json.dumps(failures))
 return records

def render_html(job,base,target,work):
 try:from playwright.sync_api import sync_playwright
 except ImportError:raise ValueError('Missing Python playwright: pip install playwright; then playwright install chromium (or configure STUDIO_BROWSER)')
 template=resolve(base,job['template']) if job.get('template') else ROOT/'examples/tandem/composition.html';html=template.read_text();validate_template(html);logs=[];frames=round(job['duration']*job['fps']);stills=work/'styleframes';stills.mkdir(exist_ok=True)
 samples=review_samples(job['duration'],job['fps'],frames,job);sample_frames={s['frame']:s for s in samples};layout=[]
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','image2pipe','-framerate',str(job['fps']),'-i','pipe:0','-an','-c:v','libx264','-preset','fast','-crf',str(job.get('crf',19)),'-pix_fmt','yuv420p','-r',str(job['fps']),'-frames:v',str(frames),'-movflags','+faststart','-map_metadata','-1',str(target)]
 with sync_playwright() as p:
  try:b=p.chromium.launch(executable_path=browser_path(),headless=True,args=['--no-sandbox','--disable-dev-shm-usage'])
  except Exception as exc:raise ValueError(f'Chromium launch failed; set STUDIO_BROWSER or run playwright install chromium: {exc}')
  page=b.new_page(viewport={'width':job['width'],'height':job['height']},device_scale_factor=1,service_workers='block');page.on('pageerror',lambda err:logs.append(str(err)));page.on('requestfailed',lambda req:logs.append('Composition resource request failed: '+req.url));page.route('**/*',lambda route:route.abort() if not route.request.url.startswith(('data:','about:')) else route.continue_());page.set_content(html,wait_until='load');template_call(page,'configure',job,job.get('renderTimeoutMs',15000));targets=layout_targets(job,page)
  for sample in samples:
   template_call(page,'seek',sample['time'],job.get('renderTimeoutMs',15000));layout.extend(inspect_layout(page,targets,sample,job.get('safeZone')))
  if logs:raise ValueError('Composition console error: '+'; '.join(logs))
  with (work/'encode.log').open('w') as log:
   proc=subprocess.Popen(cmd,stdin=subprocess.PIPE,stderr=log,stdout=subprocess.DEVNULL)
   try:
    for n in range(frames):
     t=n/job['fps'];state=template_call(page,'seek',t,job.get('renderTimeoutMs',15000));png=page.screenshot(type='png',animations='disabled',timeout=30000);proc.stdin.write(png)
     if n in sample_frames:
      (stills/f'{n:06d}.png').write_bytes(png);(stills/f'{n:06d}.json').write_text(json.dumps({'sample':sample_frames[n],'state':state},indent=2))
    proc.stdin.close();code=proc.wait()
   except BaseException:
    proc.kill();proc.wait();proc.stdin.close();raise
   if code:raise RuntimeError(f'Frame encoding failed: {(work/"encode.log").read_text()[-2000:]}')
  b.close()
 if logs:raise ValueError('Composition console error: '+'; '.join(logs))
 return {'browserErrors':logs,'layoutChecks':layout,'reviewSamples':samples,'network':'blocked','timing':'awaited configure/seek(seconds), fonts and images; integer frame sampling','maxZoom':1 if not job.get('template') else 'unverified-custom-template','sourceDensity':'vector DOM rendered at delivery pixels' if not job.get('template') else 'custom template requires source-image/zoom inspection'}

def ffescape(value):return str(value).replace('\\','/').replace(':','\\:').replace("'","'\\''")

def render_footage(job,base,target,work):
 source=resolve(base,job['source']['path']);W,H=job['width'],job['height'];portrait=H>W;margin=round(W*.06);top=round(H*(.28 if portrait else .235));areaH=round(H*(.52 if portrait else .59));areaW=W-margin*2
 font=str(resolve(base,job['font'])) if job.get('font') else next((str(p) for p in [Path('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'),Path('C:/Windows/Fonts/arial.ttf'),Path('/System/Library/Fonts/Helvetica.ttc')] if p.exists()),None)
 if not font:raise ValueError('Footage text needs a local font; set job.font to a path')
 from PIL import ImageFont
 def fits(text,size,available):
  f=ImageFont.truetype(font,size)
  if any(f.getlength(line)>available for line in text.splitlines()):raise ValueError('Footage text exceeds layout width; shorten it or author a new composition: '+text)
 fits(job['hook'],round(W*(.052 if portrait else .036)),W-2*margin)
 fits(job['cta'],round(W*.029),W-2*margin)
 for c in job.get('captions',[]):fits(c['text'],round(W*.027),W-2*margin-32)
 if job.get('safeZone'):
  z=job['safeZone']
  if z['x']>margin or z['x']+z['width']<W-margin or z['y']>H*.175 or z['y']+z['height']<H*.91:raise ValueError('Footage safeZone excludes authored caption/CTA area; author a compatible layout before rendering')
 # Text files avoid interpreting product copy as filter syntax.
 synthetic=False
 if job.get('evidence'):synthetic=json.loads(resolve(base,job['evidence']).read_text()).get('product',{}).get('synthetic',False)
 texts={'title':job['hook'],'brand':job['brand']['name']+('  /  SAMPLE WORKSPACE' if synthetic else '  /  PRODUCT WORKFLOW'),'mode':'Actual product recording'+(' · synthetic sample data' if synthetic else ''),'cta':job['cta']}
 for name,text in texts.items():(work/f'{name}.txt').write_text(text)
 filters=[]
 if job['source'].get('crop'):
  x,y,w,h=job['source']['crop'];filters.append(f'crop={w}:{h}:{x}:{y}')
 filters+=['setpts=PTS-STARTPTS',f'fps={job["fps"]}',f'scale={areaW}:{areaH}:force_original_aspect_ratio=decrease:flags=lanczos',f'pad={W}:{H}:(ow-iw)/2:{top}:color={job["brand"]["background"].replace("#","0x")}']
 for name,y,size,color in [('brand',H*(.055 if portrait else .035),W*.025,job['brand']['ink']),('title',H*(.12 if portrait else .095),W*(.052 if portrait else .036),job['brand']['ink']),('mode',H*.95,W*.019,job['brand']['ink']),('cta',H*.86,W*.029,job['brand']['accent'])]:
  filters.append(f"drawtext=fontfile='{ffescape(font)}':textfile='{ffescape(work/(name+'.txt'))}':fontcolor={color.replace('#','0x')}:fontsize={round(size)}:x={margin}:y={round(y)}")
 for n,c in enumerate(job.get('captions',[])):
  path=work/f'caption-{n}.txt';path.write_text(c['text']);filters.append(f"drawtext=fontfile='{ffescape(font)}':textfile='{ffescape(path)}':fontcolor=white:fontsize={round(W*.027)}:box=1:boxcolor=0x18251f@0.94:boxborderw=16:x=(w-tw)/2:y={round(H*(.215 if portrait else .175))}:enable='gte(t,{c['start']})*lt(t,{c['end']})'")
 args=['ffmpeg','-hide_banner','-loglevel','error','-y','-ss',str(job['source'].get('start',0)),'-i',source,'-t',str(job['duration']),'-vf',','.join(filters),'-c:v','libx264','-preset','fast','-crf',str(job.get('crf',19)),'-pix_fmt','yuv420p','-r',str(job['fps']),'-frames:v',str(round(job['fps']*job['duration']))]
 if job['source'].get('audioPolicy')=='preserve':args+=['-c:a','aac','-b:a','192k']
 else:args+=['-an']
 run(args+['-movflags','+faststart','-map_metadata','-1',target]);stream=next(s for s in probe(source)['streams'] if s['codec_type']=='video');crop=job['source'].get('crop',[0,0,stream['width'],stream['height']]);magnification=min(areaW/crop[2],areaH/crop[3])
 return {'sourceDimensions':[stream['width'],stream['height']],'sourceCrop':crop,'magnification':magnification,'sourceDensityPassed':magnification<=1,'note':'No speed changes. Actual application timing is preserved. Vertical crops require authored source.crop.'}

def mix_audio(job,base,silent,target,work):
 args=['ffmpeg','-hide_banner','-loglevel','error','-y','-i',silent];filters=[]
 for n,a in enumerate(job['audio']):
  args+=['-i',resolve(base,a['path'])];filters.append(f'[{n+1}:a]atrim=duration={a.get("duration",job["duration"]-a.get("start",0))},asetpts=PTS-STARTPTS,aresample=48000,volume={a.get("gainDb",0)}dB,adelay={round(a.get("start",0)*1000)}:all=1,apad,atrim=duration={job["duration"]}[a{n}]')
 filters.append(''.join(f'[a{n}]' for n in range(len(job['audio'])))+f'amix=inputs={len(job["audio"])}:normalize=0:duration=longest[mix]');mixed=work/'mix.wav';run(args+['-filter_complex',';'.join(filters),'-map','[mix]','-c:a','pcm_s24le',mixed]);loud=run(['ffmpeg','-hide_banner','-nostats','-i',mixed,'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']).stderr
 import re
 measured=json.loads(re.search(r'\{\s*"input_i".*?\}',loud,re.S).group(0));norm='loudnorm=I=-16:TP=-1.5:LRA=11:linear=true:measured_I={input_i}:measured_TP={input_tp}:measured_LRA={input_lra}:measured_thresh={input_thresh}:offset={target_offset}'.format(**measured)
 run(['ffmpeg','-hide_banner','-loglevel','error','-y','-i',silent,'-i',mixed,'-map','0:v:0','-map','1:a:0','-c:v','copy','-af',norm,'-c:a','aac','-b:a','192k','-t',str(job['duration']),'-movflags','+faststart','-map_metadata','-1',target]);return {'method':'two-pass loudnorm','targetLufs':-16,'maxTruePeakDbtp':-1.5,'inputMeasurement':measured}

def srt(captions):
 def stamp(s):
  ms=round(s*1000);h,ms=divmod(ms,3600000);m,ms=divmod(ms,60000);sec,ms=divmod(ms,1000);return f'{h:02}:{m:02}:{sec:02},{ms:03}'
 return '\n\n'.join(f'{i+1}\n{stamp(c["start"])} --> {stamp(c["end"])}\n{c["text"]}' for i,c in enumerate(captions))+'\n'

def receipt_assets_match(out,manifest):
 """A cached success includes every delivered review image and sidecar."""
 try:
  assets=manifest.get('assets',[])
  if not {'poster.png','captions.srt','qa.json','job.resolved.json'}.issubset({a['path'] for a in assets}):return False
  return all(digest(resolve(out,a['path']))==a['sha256'] for a in assets)
 except (ValueError,OSError,KeyError,TypeError):return False

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--job',required=True);p.add_argument('--output',required=True);p.add_argument('--preview',action='store_true',help='Render half-size, 12fps preview; source job remains unchanged.');p.add_argument('--force',action='store_true');a=p.parse_args();job_path=Path(a.job).resolve();job=json.loads(job_path.read_text());validate(job,job_path.parent);original=copy.deepcopy(job)
 if not shutil.which('ffmpeg') or not shutil.which('ffprobe'):raise ValueError('ffmpeg and ffprobe are required on PATH')
 if a.preview:
  old_w,old_h=job['width'],job['height'];job['width']=max(160,job['width']//4*2);job['height']=max(160,job['height']//4*2);job['fps']=12;job['crf']=24
  if job.get('safeZone'):
   z=job['safeZone'];job['safeZone']={'x':z['x']*job['width']/old_w,'y':z['y']*job['height']/old_h,'width':z['width']*job['width']/old_w,'height':z['height']*job['height']/old_h}
 out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True);sources=source_map(original,job_path);fingerprint=hashlib.sha256(json.dumps({'job':job,'sources':sources},sort_keys=True).encode()).hexdigest();manifest_path=out/'render-manifest.json';target=out/'video.mp4'
 if manifest_path.exists() and target.exists() and not a.force:
  old=json.loads(manifest_path.read_text())
  if old.get('fingerprint')==fingerprint and old.get('qaStatus')=='passed' and old.get('artifact',{}).get('sha256')==digest(target) and receipt_assets_match(out,old):
   qa=out/'qa.json';expected_qa=next((x['sha256'] for x in old.get('assets',[]) if x.get('path')=='qa.json'),None)
   if qa.is_file() and expected_qa==digest(qa) and json.loads(qa.read_text()).get('status')=='passed':print(json.dumps({'status':'cached','artifact':str(target),'fingerprint':fingerprint}));return 0
 manifest_path.write_text(json.dumps({'schemaVersion':'1.0.0','id':job['id'],'fingerprint':fingerprint,'sources':sources,'qaStatus':'incomplete','status':'rendering'})+'\n')
 work=out/'production';work.mkdir(exist_ok=True);silent=work/'picture.mp4';start=time.monotonic();
 if job['renderer'] in ['remotion','hyperframes']:
  if a.preview:raise ValueError('External adapter previews require an explicit preview job; no dimensions are silently substituted.')
  if job.get('audio'):raise ValueError('External adapters must own their audio; prepare an adapter project explicitly. Shared audio mixing is not applied silently.')
  adapter=ROOT/'adapters'/f'{job["renderer"]}.py';external=work/'external';result=subprocess.run([sys.executable,str(adapter),'--job',str(job_path),'--output',str(external)])
  if result.returncode:raise ValueError(f'{job["renderer"]} adapter unavailable or failed ({result.returncode}); no fallback attempted')
  if not (external/'video.mp4').is_file():raise ValueError('External adapter did not produce video.mp4')
  shutil.copy2(external/'video.mp4',silent);details={'adapter':job['renderer'],'integration':'caller-configured; unavailable adapters fail without fallback'}
 else:details=render_html(job,job_path.parent,silent,work) if job['renderer']=='html-playwright' else render_footage(job,job_path.parent,silent,work)
 audio=mix_audio(job,job_path.parent,silent,target,work) if job.get('audio') else None
 if not job.get('audio'):shutil.copy2(silent,target)
 (out/'captions.srt').write_text(srt(job.get('captions',[])));(out/'job.resolved.json').write_text(json.dumps(job,indent=2)+'\n');report=inspect(target,job,out/'review');(out/'qa.json').write_text(json.dumps(report,indent=2)+'\n');run(['ffmpeg','-v','error','-ss',str(min(5,job['duration']*.5)),'-i',target,'-frames:v','1','-c:v','png','-pix_fmt','rgb24','-threads','1','-y',out/'poster.png'])
 asset_paths=['poster.png','captions.srt','qa.json','job.resolved.json']+['review/'+entry['path'] for entry in report.get('reviewFrames',[])+report.get('reviewSheets',[])]
 for sample in details.get('reviewSamples',[]):
  asset_paths.extend(f'production/styleframes/{sample["frame"]:06d}.'+suffix for suffix in ['png','json'])
 manifest={'schemaVersion':'1.0.0','id':job['id'],'renderer':job['renderer'],'productRevision':job['productRevision'],'visualMode':job['visualMode'],'preview':a.preview,'fingerprint':fingerprint,'sources':sources,'artifact':{'path':'video.mp4','sha256':digest(target)},'assets':[{'path':n,'sha256':digest(out/n)} for n in dict.fromkeys(asset_paths)],'duration':job['duration'],'frameCount':round(job['duration']*job['fps']),'dimensions':[job['width'],job['height']],'claimIds':job.get('claimIds',[]),'audioMix':audio,'implementationChecks':details,'qaStatus':report['status'],'elapsedSeconds':round(time.monotonic()-start,2),'creativeReview':'required; inspect decoded final video and frames'};manifest_path.write_text(json.dumps(manifest,indent=2)+'\n');print(json.dumps({'status':report['status'],'artifact':str(target),'fingerprint':fingerprint,'elapsedSeconds':manifest['elapsedSeconds']}));return 0 if report['status']=='passed' else 1
if __name__=='__main__':
 try:sys.exit(main())
 except (ValueError,RuntimeError,FileNotFoundError,KeyError) as exc:print(json.dumps({'status':'failed','error':str(exc)}),file=sys.stderr);sys.exit(2)
