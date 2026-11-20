#!/usr/bin/env python3
"""Explicit optional HyperFrames integration via a caller-verified argument vector."""
import argparse,json,shutil,subprocess,sys
from pathlib import Path

def main():
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--job',required=True);p.add_argument('--output',required=True);a=p.parse_args();jp=Path(a.job).resolve();j=json.loads(jp.read_text());spec=j.get('hyperframes',{});command=spec.get('command')
 if not isinstance(command,list) or not command or not all(isinstance(v,str) for v in command):raise ValueError('HyperFrames adapter unavailable: provide hyperframes.command as the installed renderer’s verified argument vector. No guessed CLI or fallback is used.')
 if not shutil.which(command[0]) and not Path(command[0]).is_file():raise ValueError('HyperFrames executable unavailable: '+command[0])
 out=Path(a.output).resolve();out.mkdir(parents=True,exist_ok=True);values={'{job}':str(jp),'{output}':str(out/'video.mp4')};args=[values.get(v,v) for v in command]
 if '{output}' not in command:raise ValueError('Command must contain a separate {output} argument to bind the output location.')
 result=subprocess.run(args,cwd=jp.parent)
 if result.returncode:return result.returncode
 if not (out/'video.mp4').is_file():raise ValueError('HyperFrames command did not produce the contracted video.mp4')
 print(json.dumps({'status':'rendered','renderer':'hyperframes','note':'Caller-supplied integration; not verified in this environment.'}));return 0
if __name__=='__main__':
 try:sys.exit(main())
 except (ValueError,FileNotFoundError) as e:print(json.dumps({'status':'unavailable','error':str(e)}),file=sys.stderr);sys.exit(2)
