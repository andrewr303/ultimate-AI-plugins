#!/usr/bin/env python3
"""Inspect the delivered encoding and create decoded-frame review artifacts. No taste score."""
from __future__ import annotations
import argparse,hashlib,json,math,re,subprocess,sys,tempfile,textwrap
from pathlib import Path

def run(args,check=True):
 p=subprocess.run([str(a) for a in args],capture_output=True,text=True)
 if check and p.returncode: raise RuntimeError(f'{args[0]} failed ({p.returncode}): {p.stderr[-2000:]}')
 return p

def digest(path):
 h=hashlib.sha256()
 with Path(path).open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 return h.hexdigest()

def probe(path):
 return json.loads(run(['ffprobe','-v','error','-count_frames','-show_streams','-show_format','-of','json',path]).stdout)

def fraction(v):
 a,b=v.split('/') if '/' in v else (v,'1');return float(a)/float(b) if float(b) else 0

MAX_REVIEW_SAMPLES = 512
REVIEW_SHEET_SIZE = 24

def review_samples(duration, fps, frame_count, expected=None):
 """Select exact encoded frame indices; job labels are metadata, never paths/code."""
 def number(value, name):
  if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
   raise ValueError(f'{name} must be a finite number')
  return value
 if number(duration, 'duration') <= 0 or number(fps, 'fps') <= 0:
  raise ValueError('Review duration and fps must be positive')
 if isinstance(frame_count, bool) or not isinstance(frame_count, int) or frame_count < 1:
  raise ValueError('Review requires a positive decoded frame count')
 if expected is not None and not isinstance(expected, dict):
  raise ValueError('Review job must be an object')
 expected = expected or {}
 points = expected.get('reviewPoints', [])
 captions = expected.get('captions', [])
 if not isinstance(points, list) or len(points) > 32:
  raise ValueError('reviewPoints must be an array with at most 32 entries')
 if not isinstance(captions, list) or len(captions) > 100:
  raise ValueError('captions must be an array with at most 100 entries for review')
 selected = {}
 def add(frame, label, clamp=False):
  if clamp:
   frame = min(frame_count - 1, max(0, frame))
  if frame < 0 or frame >= frame_count:
   return
  labels = selected.setdefault(frame, [])
  if label not in labels:
   labels.append(label)
  if len(selected) > MAX_REVIEW_SAMPLES:
   raise ValueError(f'Review exceeds {MAX_REVIEW_SAMPLES} unique frames; split the job or reduce captions/review points')
 def at(seconds):
  return math.floor(seconds * fps + 1e-9)
 add(0, 'opening')
 add(frame_count - 1, 'ending')
 for portion in (.25, .5, .75):
  add(at(duration * portion), f'timeline-{round(portion * 100)}%', clamp=True)
 for i, point in enumerate(points):
  if not isinstance(point, dict) or set(point) != {'time', 'label'}:
   raise ValueError(f'reviewPoints[{i}] requires only time and label')
  t = number(point['time'], f'reviewPoints[{i}].time')
  label = point['label']
  if not isinstance(label, str) or not label.strip() or len(label) > 80:
   raise ValueError(f'reviewPoints[{i}].label must contain 1..80 characters')
  if not 0 <= t < duration:
   raise ValueError(f'reviewPoints[{i}].time must be inside the video duration')
  add(at(t), label, clamp=True)
 for i, caption in enumerate(captions):
  if not isinstance(caption, dict) or not {'start', 'end'}.issubset(caption):
   raise ValueError(f'captions[{i}] requires start and end')
  start = number(caption['start'], f'captions[{i}].start')
  end = number(caption['end'], f'captions[{i}].end')
  if not 0 <= start < end <= duration:
   raise ValueError(f'captions[{i}] must start before end inside the video duration')
  prefix = f'caption-{i + 1}'
  add(at((start + end) / 2), prefix + ':midpoint', clamp=True)
  # Ceil locates the first frame at/after the boundary. Unlike clamping,
  # skipping unavailable neighbours does not label the last active frame inactive.
  for t, boundary in [(start, 'start'), (end, 'end')]:
   frame = math.ceil(t * fps - 1e-9)
   for offset, label in [(-1, 'before-'), (0, ''), (1, 'after-')]:
    add(frame + offset, prefix + ':' + label + boundary)
 return [{'frame': frame, 'time': frame / fps, 'labels': selected[frame]} for frame in sorted(selected)]

def extract_review(path, samples, review_dir):
 """Decode selected frames once, then build bounded contact-sheet pages."""
 from PIL import Image,ImageDraw
 rd = Path(review_dir)
 rd.mkdir(parents=True, exist_ok=True)
 review, sheets, tiles = [], [], []
 expression = '+'.join(f'eq(n\\,{sample["frame"]})' for sample in samples)
 with tempfile.TemporaryDirectory(prefix='.review-', dir=rd) as temporary:
  pattern = Path(temporary) / '%06d.png'
  run(['ffmpeg', '-v', 'error', '-i', path, '-map', '0:v:0', '-vf', 'select=' + expression,
       '-fps_mode', 'vfr', '-frames:v', str(len(samples)), '-c:v', 'png', '-pix_fmt', 'rgb24',
       '-threads', '1', '-start_number', '0', '-y', pattern])
  for index, sample in enumerate(samples):
   decoded = Path(temporary) / f'{index:06d}.png'
   if not decoded.is_file():
    raise ValueError(f'Decoder did not produce requested review frame {sample["frame"]}')
   target = rd / f'frame-{sample["frame"]:06d}.png'
   decoded.replace(target)
   with Image.open(target) as source:
    image = source.convert('RGB')
   image.thumbnail((440, 340))
   tile = Image.new('RGB', (460, 420), '#f4f1e9')
   tile.paste(image, ((460 - image.width) // 2, 10))
   draw = ImageDraw.Draw(tile)
   draw.text((14, 355), f'Frame {sample["frame"]} | {sample["time"]:.6f}s | decoded MP4', fill='#18251f')
   # Plain-text preview is clipped to the tile; full Unicode labels remain in QA.
   label = ' / '.join(' '.join(item.split()) for item in sample['labels'])
   label = label.encode('ascii', 'replace').decode('ascii')
   for line_number, line in enumerate(textwrap.wrap(label, 68)[:3]):
    draw.text((14, 373 + line_number * 13), line, fill='#18251f')
   tiles.append(tile)
   review.append({**sample, 'path': target.name, 'sha256': digest(target)})
   if len(tiles) == REVIEW_SHEET_SIZE or index == len(samples) - 1:
    sheet = Image.new('RGB', (460 * 3, 420 * math.ceil(len(tiles) / 3)), '#e8e8df')
    for tile_number, current in enumerate(tiles):
     sheet.paste(current, ((tile_number % 3) * 460, (tile_number // 3) * 420))
    name = 'contact-sheet.jpg' if not sheets else f'contact-sheet-{len(sheets) + 1:03d}.jpg'
    sheet.save(rd / name, quality=91)
    sheets.append({'path': name, 'sha256': digest(rd / name)})
    tiles.clear()
 current_paths = {entry['path'] for entry in review + sheets}
 for previous in rd.iterdir():
  if previous.is_file() and re.fullmatch(r'(?:frame-\d{6,}\.png|contact-sheet(?:-\d{3,})?\.jpg)', previous.name) and previous.name not in current_paths:
   previous.unlink()
 return review, sheets

def inspect(path,expected=None,review_dir=None):
 path=Path(path);p=probe(path);v=next((s for s in p['streams'] if s['codec_type']=='video'),None)
 if not v:raise ValueError('No video stream')
 a=next((s for s in p['streams'] if s['codec_type']=='audio'),None);checks=[]
 def check(name,ok,detail):checks.append({'name':name,'status':'passed' if ok else 'failed','detail':detail})
 duration=float(p['format']['duration']);fps=fraction(v['avg_frame_rate']);frames=int(v.get('nb_read_frames',v.get('nb_frames','0')))
 sampling_duration=expected.get('duration',duration) if isinstance(expected,dict) else duration
 samples=review_samples(sampling_duration,fps,frames,expected)
 check('video-stream',v['codec_name']=='h264' and v.get('pix_fmt')=='yuv420p',{'codec':v['codec_name'],'pixelFormat':v.get('pix_fmt')})
 args=['ffmpeg','-hide_banner','-nostats','-v','info','-xerror','-i',path,'-map','0:v:0','-vf','blackdetect=d=0.15:pic_th=0.98:pix_th=0.05']
 if a:args+=['-map','0:a:0','-af','ebur128=peak=true']
 decoded=run(args+['-f','null','-'],check=False);black=[{'start':float(m[0]),'end':float(m[1]),'duration':float(m[2])} for m in re.findall(r'black_start:([\d.]+) black_end:([\d.]+) black_duration:([\d.]+)',decoded.stderr)]
 check('full-decode',decoded.returncode==0,decoded.stderr[-1200:] if decoded.returncode else {'decodedFrames':frames})
 check('black-intervals',not black,black)
 if expected:
  check('dimensions',(v['width'],v['height'])==(expected['width'],expected['height']),{'actual':[v['width'],v['height']],'expected':[expected['width'],expected['height']]})
  check('frame-rate',abs(fps-expected['fps'])<.001,{'actual':fps,'expected':expected['fps']})
  check('duration',abs(duration-expected['duration'])<=1/expected['fps']+.025,{'actual':duration,'expected':expected['duration']})
  check('frame-count',frames==round(expected['duration']*expected['fps']),{'actual':frames,'expected':round(expected['duration']*expected['fps'])})
  check('audio-presence',bool(a)==(bool(expected.get('audio')) or expected.get('source',{}).get('audioPolicy')=='preserve'),{'present':bool(a),'requested':bool(expected.get('audio'))})
 audio={'status':'not-requested','reason':'Intentional sound-off creative; no audio stream was requested.'}
 if a:
  loud=run(['ffmpeg','-hide_banner','-nostats','-i',path,'-af','loudnorm=I=-16:TP=-1.5:LRA=11:print_format=json','-f','null','-']).stderr
  m=re.search(r'\{\s*"input_i".*?\}',loud,re.S);measured=json.loads(m.group(0)) if m else {}
  audio={'status':'measured','integratedLufs':measured.get('input_i'),'truePeakDbtp':measured.get('input_tp'),'targetLufs':-16,'maxTruePeakDbtp':-1.0}
  check('audio-true-peak',float(measured.get('input_tp','inf'))<=-1.0,audio)
  check('audio-loudness',abs(float(measured.get('input_i','inf'))+16)<=1.5,audio)
 review=[];sheets=[]
 if review_dir:
  review,sheets=extract_review(path,samples,review_dir)
 return {'schemaVersion':'1.0.0','artifact':path.name,'sha256':digest(path),'dimensions':[v['width'],v['height']],'fps':fps,'duration':duration,'frames':frames,'audio':audio,'checks':checks,'status':'passed' if all(c['status']=='passed' for c in checks) else 'failed','visualReview':{'status':'required','reason':'Open decoded contact sheets and inspect playback; mechanical checks do not judge persuasion or readable typography.'},'reviewFrames':review,'reviewSheets':sheets}

def main():
 p=argparse.ArgumentParser(description=__doc__);sub=p.add_subparsers(dest='command',required=True);q=sub.add_parser('inspect');q.add_argument('file');q.add_argument('--output');q.add_argument('--review-dir');q.add_argument('--job');a=p.parse_args();expected=json.loads(Path(a.job).read_text()) if a.job else None;result=inspect(a.file,expected,a.review_dir);text=json.dumps(result,indent=2)
 if a.output:Path(a.output).parent.mkdir(parents=True,exist_ok=True);Path(a.output).write_text(text+'\n')
 print(text);return 0 if result['status']=='passed' else 1
if __name__=='__main__':
 try:sys.exit(main())
 except (ValueError,RuntimeError,FileNotFoundError) as exc:print(json.dumps({'status':'failed','error':str(exc)}),file=sys.stderr);sys.exit(2)
