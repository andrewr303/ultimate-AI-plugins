#!/usr/bin/env python3
"""Explicit optional local Remotion bridge. Uses an already-installed CLI; never downloads it."""
import argparse,json,os,subprocess,sys
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--job',required=True);p.add_argument('--output',required=True);a=p.parse_args();jp=Path(a.job).resolve();j=json.loads(jp.read_text());spec=j.get('remotion',{});project=(jp.parent/spec.get('project','.')).resolve();binary=project/'node_modules'/'.bin'/('remotion.cmd' if os.name=='nt' else 'remotion');entry=(project/spec.get('entry','src/index.ts')).resolve()
 if not binary.is_file():raise ValueError('Remotion unavailable: install and license Remotion in your adapter project. No fallback was attempted.')
 if not entry.is_file() or not spec.get('composition'):raise ValueError('Set remotion.entry and remotion.composition to your registered composition.')
 output=Path(a.output).resolve();output.mkdir(parents=True,exist_ok=True)
 args=[str(binary),'render',str(entry),spec['composition'],str(output/'video.mp4'),'--props',str(jp),'--codec','h264','--pixel-format','yuv420p','--fps',str(j['fps']),'--width',str(j['width']),'--height',str(j['height']),'--frames',f'0-{round(j["duration"]*j["fps"])-1}']
 result=subprocess.run(args,cwd=project)
 if result.returncode:return result.returncode
 print(json.dumps({'status':'rendered','renderer':'remotion','note':'Run scripts/media.py inspect on the resulting MP4; adapter not exercised in this build.'}));return 0
if __name__=='__main__':
 try:sys.exit(main())
 except (ValueError,FileNotFoundError) as e:print(json.dumps({'status':'unavailable','error':str(e)}),file=sys.stderr);sys.exit(2)
