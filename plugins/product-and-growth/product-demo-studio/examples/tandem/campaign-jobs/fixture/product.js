/* Local synthetic product fixture. No external requests, persistence or outbound actions. */
'use strict';
(() => {
  const samples = {
    billing: {name:'Jamie Lee', initials:'JL', subject:'Charged twice?', time:'2m', message:'I think I was charged twice for my order. Could someone check the two payments on my account? I only placed one order.'},
    access: {name:'River Quinn', initials:'RQ', subject:'Can’t sign in', time:'8m', message:'I cannot sign in to my account. I tried resetting my password, but the reset email has not arrived.'},
    general: {name:'Morgan Park', initials:'MP', subject:'A product question', time:'14m', message:'Hello! Where can I find the guide to getting started with the product?'}
  };
  class DemoMachine {
    constructor(onChange){this.onChange=onChange;this.timer=null;this.state='initial';this.case='billing';this.failOnce=false;}
    set(state){this.state=state;this.onChange(state);}
    cancel(){clearTimeout(this.timer);this.timer=null;this.set('input');}
    reset(){clearTimeout(this.timer);this.timer=null;this.failOnce=false;this.set('initial');}
    run(value, forceSuccess=false){
      clearTimeout(this.timer);
      if(!value.trim()){this.set('empty');return;}
      this.set('loading');
      this.timer=setTimeout(()=>{
        this.timer=null;
        if(this.case==='error'&&!forceSuccess&&!this.failOnce){this.failOnce=true;this.set('error');return;}
        this.set('success');
      },850);
    }
  }
  window.TandemDemoMachine=DemoMachine;
  class TandemWorkspace extends HTMLElement {
    connectedCallback(){
      if(this.dataset.initialized)return;this.dataset.initialized='true';this.selected='billing';
      this.innerHTML=`<div class="workspace-shell"><div class="workspace-topbar"><span class="workspace-name"><span class="mini-mark" aria-hidden="true">t.</span> Support workspace</span><span class="sample-label">SYNTHETIC DATA</span></div><div class="workspace-body"><aside class="inbox-sidebar" aria-label="Sample inbox"><div class="sidebar-heading">Inbox <span class="inbox-count">3</span></div><label class="inbox-search-label"><span aria-hidden="true">⌕</span><input class="inbox-search" id="inbox-search" type="search" aria-label="Search sample requests" placeholder="Find a request…" autocomplete="off"></label><ul class="inbox-items">${Object.entries(samples).map(([key,item])=>`<li data-sample="${key}"><button class="inbox-item" type="button" data-case="${key}" aria-pressed="${key==='billing'}"><span class="inbox-name"><span><i class="inbox-dot" aria-hidden="true"></i>${item.name}</span><span class="inbox-time">${item.time}</span></span><span class="inbox-subject">${item.subject}</span></button></li>`).join('')}</ul><p class="inbox-empty" hidden>No matching requests.<br><button class="text-button" type="button" data-clear-search>Clear search</button></p><p class="sidebar-footer">SAMPLE WORKSPACE<br>All names and requests are synthetic.</p></aside><section class="workspace-content" aria-label="Selected support request"><div class="request-topline"><span>REQUEST / #1042</span><span class="local-indicator"><i aria-hidden="true"></i> Local only</span></div><h2 class="request-title">Charged twice?</h2><div class="message-person"><span class="avatar" data-person-initials>JL</span><span><strong data-person-name>Jamie Lee</strong><small>Synthetic customer · Sample message</small></span></div><label class="input-label" for="message-input">Original request <span aria-hidden="true"><svg class="icon-arrow" aria-hidden="true" viewBox="0 0 20 20"><path d="M4 16 16 4M4 4h12v12"/></svg></span></label><textarea class="message-input" id="message-input" spellcheck="false" maxlength="2000">${samples.billing.message}</textarea><div class="sample-controls"><label for="sample-select">Try another scenario</label><select id="sample-select" class="sample-select"><option value="billing">Billing request</option><option value="access">Account access</option><option value="general">General question</option><option value="empty">Empty request</option><option value="error">Simulate a failure</option></select></div><div class="triage-action"><button class="triage-button" id="triage-button" type="button">Organize request <span aria-hidden="true"><svg class="icon-arrow" aria-hidden="true" viewBox="0 0 20 20"><path d="M4 16 16 4M4 4h12v12"/></svg></span></button><button class="cancel-button" id="cancel-demo" type="button" hidden>Cancel</button><button class="reset-button" id="reset-demo" type="button">Reset </button></div><p class="workspace-status" id="workspace-status" role="status" aria-live="polite" data-state="initial">Choose a sample, or edit the request. Then organize it.</p><div class="error-controls" hidden><button class="retry-button" id="retry-demo" type="button">Try again</button><span class="fine-print">The retry succeeds locally.</span></div><section class="result-panel" id="result-panel" aria-label="Suggested route and reply" hidden><div class="result-heading"><strong>A clearer next step</strong><span>Deterministic suggestion</span></div><div class="route-chips"><span class="route-category" id="route-category">Billing</span><span id="route-priority">Priority: high</span><span id="route-owner">Owner: Alex</span></div><label class="input-label" for="reply-output">Suggested reply <span>Editable</span></label><textarea class="reply-output" id="reply-output" spellcheck="false" maxlength="3000"></textarea><div class="review-actions"><button class="approve-button" id="approve-button" type="button">Mark ready for review </button><p class="result-disclosure">Nothing is sent.<br>You make the next move.</p></div></section></section></div></div>`;
      this.$=s=>this.querySelector(s);this.machine=new DemoMachine(state=>this.renderState(state));
      this.$('#message-input').addEventListener('input',()=>{this.machine.cancel();this.machine.set('input');});
      this.$('#triage-button').addEventListener('click',()=>this.machine.run(this.$('#message-input').value));
      this.$('#cancel-demo').addEventListener('click',()=>this.machine.cancel());
      this.$('#reset-demo').addEventListener('click',()=>this.reset());
      this.$('#retry-demo').addEventListener('click',()=>this.machine.run(this.$('#message-input').value,true));
      this.$('#sample-select').addEventListener('change',e=>this.selectSample(e.target.value));
      this.$('#approve-button').addEventListener('click',()=>{this.$('#approve-button').textContent='Ready for review ';this.$('#approve-button').disabled=true;this.$('#workspace-status').textContent='Draft marked ready for review. No message was sent.';this.dataset.review='ready';});
      this.$('#reply-output').addEventListener('input',()=>{this.$('#approve-button').disabled=false;this.$('#approve-button').textContent='Mark ready for review ';this.dataset.review='draft';});
      this.querySelectorAll('[data-case]').forEach(button=>button.addEventListener('click',()=>this.selectSample(button.dataset.case)));
      this.$('#inbox-search').addEventListener('input',()=>this.filterInbox());this.$('[data-clear-search]').addEventListener('click',()=>{this.$('#inbox-search').value='';this.filterInbox();this.$('#inbox-search').focus();});
      this.dataset.state='initial';
    }
    disconnectedCallback(){if(this.machine)clearTimeout(this.machine.timer);}
    selectSample(key){
      this.machine.cancel();this.machine.case=key;this.machine.failOnce=false;this.selected=key;
      const item=samples[key]||samples.billing;
      this.$('#sample-select').value=key;
      this.$('#message-input').value=key==='empty'?'':item.message;
      this.$('.request-title').textContent=key==='error'?'A recoverable failure':key==='empty'?'Start with a request':item.subject;
      this.$('[data-person-name]').textContent=item.name;this.$('[data-person-initials]').textContent=item.initials;
      this.querySelectorAll('[data-case]').forEach(button=>button.setAttribute('aria-pressed',String(button.dataset.case===key)));
      this.machine.set('input');
    }
    filterInbox(){const q=this.$('#inbox-search').value.toLowerCase().trim();let count=0;this.querySelectorAll('[data-sample]').forEach(li=>{const item=samples[li.dataset.sample];const visible=`${item.name} ${item.subject} ${item.message}`.toLowerCase().includes(q);li.hidden=!visible;if(visible)count++;});this.$('.inbox-empty').hidden=count>0;this.$('.inbox-count').textContent=String(count);}
    reset(){this.selectSample('billing');this.$('#inbox-search').value='';this.filterInbox();this.machine.reset();this.dataset.review='draft';}
    renderState(state){
      this.dataset.state=state;this.$('#result-panel').hidden=state!=='success';this.$('.error-controls').hidden=state!=='error';this.$('#cancel-demo').hidden=state!=='loading';this.$('#triage-button').disabled=state==='loading';this.$('#sample-select').disabled=state==='loading';this.$('#message-input').readOnly=state==='loading';
      const status={initial:'Choose a sample, or edit the request. Then organize it.',input:'Request changed. Organize it when you’re ready.',loading:'Organizing the sample request…',success:'Route and draft ready. Review and edit before the next step.',empty:'Add a request first. There is nothing to organize yet.',error:'The sample operation failed. Try again or choose another scenario.'};
      this.$('#workspace-status').textContent=status[state];this.$('#workspace-status').dataset.state=state;
      this.$('#triage-button').innerHTML=state==='loading'?'<span class="processing-mark" aria-hidden="true"></span> Organizing…':'Organize request <span aria-hidden="true"><svg class="icon-arrow" aria-hidden="true" viewBox="0 0 20 20"><path d="M4 16 16 4M4 4h12v12"/></svg></span>';
      if(state==='success'){
        const value=this.$('#message-input').value.toLowerCase();let route='General support',priority='normal',owner='Morgan',reply='Thanks for your message. I’ll share your question with our support team and follow up with a useful next step.';
        if(/charg|bill|payment|refund/.test(value)){route='Billing';priority='high';owner='Alex';reply='Hi Jamie, thanks for flagging this. I’ll ask our billing team to review the two payments and follow up with you.';}
        else if(/sign|password|access|login/.test(value)){route='Account access';priority='high';owner='Sam';reply='Hi River, thanks for letting us know. I’ll ask our account team to check the reset email and help you regain access.';}
        this.$('#route-category').textContent=route;this.$('#route-priority').textContent=`Priority: ${priority}`;this.$('#route-owner').textContent=`Owner: ${owner}`;this.$('#reply-output').value=reply;this.$('#approve-button').disabled=false;this.$('#approve-button').textContent='Mark ready for review ';this.dataset.review='draft';
      }
      this.dispatchEvent(new CustomEvent('tandem:state',{detail:{state},bubbles:true}));
    }
  }
  customElements.define('tandem-workspace',TandemWorkspace);
  document.querySelectorAll('[data-tabs]').forEach(group=>{
    const tabs=[...group.querySelectorAll('[role=tab]')];
    function activate(tab,focus=false){tabs.forEach(t=>{const selected=t===tab;t.setAttribute('aria-selected',String(selected));t.tabIndex=selected?0:-1;document.getElementById(t.getAttribute('aria-controls')).hidden=!selected;});if(focus)tab.focus();}
    tabs.forEach((tab,index)=>{tab.addEventListener('click',()=>activate(tab));tab.addEventListener('keydown',e=>{let next;if(e.key==='ArrowRight')next=(index+1)%tabs.length;if(e.key==='ArrowLeft')next=(index-1+tabs.length)%tabs.length;if(e.key==='Home')next=0;if(e.key==='End')next=tabs.length-1;if(next!==undefined){e.preventDefault();activate(tabs[next],true);}});});
  });
  document.querySelectorAll('[data-comparison]').forEach(input=>input.addEventListener('input',()=>{document.getElementById(input.dataset.comparison).style.setProperty('--reveal',`${input.value}%`);document.getElementById('comparison-value').textContent=`${input.value}%`;}));
  document.querySelectorAll('[data-reorder]').forEach(list=>{
    const original=[...list.children];let dragId=null;
    function announce(text){const target=list.parentElement.querySelector('.queue-status');if(target)target.textContent=text;}
    function update(){const items=[...list.children];items.forEach((li,i)=>{li.querySelector('[data-move="-1"]').disabled=i===0;li.querySelector('[data-move="1"]').disabled=i===items.length-1;});}
    list.addEventListener('click',e=>{const button=e.target.closest('[data-move]');if(!button)return;const li=button.closest('li');const direction=Number(button.dataset.move);const other=direction<0?li.previousElementSibling:li.nextElementSibling;if(!other)return;if(direction<0)list.insertBefore(li,other);else list.insertBefore(other,li);update();const nextFocus=li.querySelector(button.disabled?'[data-move]:not([disabled])':`[data-move="${direction}"]`);if(nextFocus)nextFocus.focus();announce(`${li.querySelector('strong').textContent} moved to position ${[...list.children].indexOf(li)+1}.`);});
    list.addEventListener('dragstart',e=>{const li=e.target.closest('li');if(!li)return;dragId=li.dataset.id;li.classList.add('dragging');e.dataTransfer.effectAllowed='move';e.dataTransfer.setData('text/plain',dragId);});
    list.addEventListener('dragover',e=>{const li=e.target.closest('li');if(!li||li.dataset.id===dragId)return;e.preventDefault();li.classList.add('drag-over');});
    list.addEventListener('dragleave',e=>e.target.closest('li')?.classList.remove('drag-over'));
    list.addEventListener('drop',e=>{e.preventDefault();const target=e.target.closest('li'),source=[...list.children].find(li=>li.dataset.id===dragId);if(source&&target&&source!==target){const rect=target.getBoundingClientRect();list.insertBefore(source,e.clientY<rect.top+rect.height/2?target:target.nextSibling);announce(`${source.querySelector('strong').textContent} moved to position ${[...list.children].indexOf(source)+1}.`);}list.querySelectorAll('.drag-over').forEach(li=>li.classList.remove('drag-over'));update();});
    list.addEventListener('dragend',()=>{dragId=null;list.querySelectorAll('.dragging,.drag-over').forEach(li=>li.classList.remove('dragging','drag-over'));});
    document.querySelector('[data-reset-queue]')?.addEventListener('click',()=>{original.forEach(li=>list.appendChild(li));update();announce('Original sample order restored.');});update();
  });
})();
