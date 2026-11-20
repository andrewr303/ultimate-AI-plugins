/* Scrollcraft-informed normalized progress; independently implemented for this bounded UI story.
   Semantic DOM owns content. Scroll samples state, with no persistent animation loop. */
'use strict';
(() => {
  const root=document.querySelector('[data-scroll-story]');if(!root)return;
  const buttons=[...root.querySelectorAll('[data-stage]')],visual=root.querySelector('[data-story-state]');
  const reduced=matchMedia('(prefers-reduced-motion: reduce)');let scheduled=false,visible=false,current=-1,manual=false,replayTimers=[];
  const replay=document.querySelector('[data-replay-story]'),replayStatus=document.querySelector('.replay-status');
  function stopReplay(){replayTimers.forEach(clearTimeout);replayTimers=[];if(replay)replay.textContent='Replay the handoff';}
  function show(stage){stage=Math.max(0,Math.min(buttons.length-1,stage));if(current===stage)return;current=stage;visual.dataset.storyState=String(stage);visual.style.setProperty('--story-progress',String(stage/(buttons.length-1)));buttons.forEach((b,i)=>{b.classList.toggle('active',i===stage);b.setAttribute('aria-pressed',String(i===stage));});root.dataset.visibleState=String(stage);}
  function readScroll(){scheduled=false;if(!visible||reduced.matches||manual)return;const center=innerHeight*.52;let index=0,distance=Infinity;buttons.forEach((button,i)=>{const rect=button.getBoundingClientRect();const d=Math.abs(rect.top+rect.height*.5-center);if(d<distance){distance=d;index=i;}});show(index);}
  function schedule(){if(scheduled||!visible||reduced.matches||manual)return;scheduled=true;requestAnimationFrame(readScroll);}
  function resumeScroll(){stopReplay();manual=false;schedule();}
  const observer=new IntersectionObserver(entries=>{visible=entries[0].isIntersecting;root.dataset.offscreen=String(!visible);if(visible)schedule();else stopReplay();},{rootMargin:'80px'});observer.observe(root);
  buttons.forEach((button,i)=>button.addEventListener('click',()=>{stopReplay();manual=true;show(i);}));
  replay?.addEventListener('click',()=>{if(replayTimers.length){stopReplay();if(replayStatus)replayStatus.textContent='Replay stopped. Choose a step to continue.';return;}manual=true;show(0);if(reduced.matches){if(replayStatus)replayStatus.textContent='Reduced motion is enabled. Choose each step to move through the handoff.';return;}replay.textContent='Stop replay';if(replayStatus)replayStatus.textContent='Receive, route, then review.';replayTimers=[setTimeout(()=>show(1),1100),setTimeout(()=>show(2),2200),setTimeout(()=>{stopReplay();if(replayStatus)replayStatus.textContent='Handoff complete. Replay or choose any step.';},3300)];});
  addEventListener('scroll',schedule,{passive:true});addEventListener('resize',schedule,{passive:true});
  addEventListener('wheel',resumeScroll,{passive:true});addEventListener('touchmove',resumeScroll,{passive:true});addEventListener('keydown',e=>{if(['ArrowUp','ArrowDown','PageUp','PageDown','Home','End',' '].includes(e.key)&&!['INPUT','TEXTAREA','SELECT'].includes(document.activeElement?.tagName))resumeScroll();});
  reduced.addEventListener('change',()=>{stopReplay();show(reduced.matches?2:0);schedule();});
  show(reduced.matches?2:0);
  window.TandemStory={show,readScroll,resumeScroll,get state(){return current;},get visible(){return visible;}};
})();
