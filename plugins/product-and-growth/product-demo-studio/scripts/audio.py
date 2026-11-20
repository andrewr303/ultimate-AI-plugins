#!/usr/bin/env python3
"""Generate a modest original demo underscore and measured cue sheet; no samples or providers."""
import argparse,json,math,struct,wave
from pathlib import Path
RATE=48000

def compose(path,duration=12):
 # A quiet original four-note motif, two warm partials, and restrained click transients.
 # This is an editable production fixture, not a licensed commercial soundtrack.
 notes=[220.0,261.6256,329.6276,293.6648];samples=[];peaks=[]
 for i in range(round(duration*RATE)):
  t=i/RATE;beat=math.floor(t/.5);phase=t-beat*.5;freq=notes[(beat//2)%4];env=(1-math.exp(-phase*80))*math.exp(-phase*4.5)
  tone=(math.sin(2*math.pi*freq*phase)+.28*math.sin(2*math.pi*freq*2*phase))*env*.15
  low=math.sin(2*math.pi*110*t)*.025*min(1,t/.1)*min(1,(duration-t)/.2)
  click=0
  for at in [2.8,4.1,8.7]:
   dt=t-at
   if 0<=dt<.08:click+=math.sin(2*math.pi*(720-240*dt/.08)*dt)*math.exp(-dt*70)*.1
  value=(tone+low+click)*min(1,t/.07)*min(1,(duration-t)/.3);samples.append(max(-32767,min(32767,round(value*32767))))
 path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
 with wave.open(str(path),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(RATE);w.writeframes(struct.pack('<'+'h'*len(samples),*samples))
 cue={'schemaVersion':'1.0.0','asset':path.name,'rightsId':'original-demo-score','rights':'Original programmatic composition; no third-party recordings, melodies or samples. Plugin demonstration asset.','sampleRate':RATE,'duration':duration,'peakDbfs':round(20*math.log10(max(abs(x) for x in samples)/32767),2),'bpm':120,'beats':[round(x*.5,3) for x in range(math.ceil(duration/.5))],'actionCues':[{'time':2.8,'event':'request-triage'},{'time':4.1,'event':'suggestion-arrives'},{'time':8.7,'event':'approve-draft'}]};path.with_suffix('.json').write_text(json.dumps(cue,indent=2)+'\n');return cue
if __name__=='__main__':
 p=argparse.ArgumentParser(description=__doc__);p.add_argument('--output',required=True);p.add_argument('--duration',type=float,default=12);a=p.parse_args()
 if not 1<=a.duration<=180:p.error('duration must be 1..180 seconds')
 print(json.dumps(compose(a.output,a.duration)))
