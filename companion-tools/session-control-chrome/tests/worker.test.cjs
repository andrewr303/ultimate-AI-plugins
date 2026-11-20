const {test}=require('node:test');
const assert=require('node:assert/strict');
test('toolbar opens/reuses the dashboard; session routing stays account-bound',async()=>{
  const {sampleState}=await import('../extension/model.js');const state=sampleState();
  const listeners={},calls=[];let contexts=[];
  const event=name=>({addListener:fn=>{listeners[name]=fn;}});
  global.chrome={
    action:{onClicked:event('click')},commands:{onCommand:event('command')},
    runtime:{id:'a'.repeat(32),getURL:p=>`chrome-extension://${'a'.repeat(32)}/${p}`,getContexts:async()=>contexts,onInstalled:event('install'),onMessage:event('message'),sendNativeMessage:(host,msg,cb)=>{calls.push({native:msg});cb({ok:true});}},
    storage:{local:{get:async()=>({state}),setAccessLevel:async()=>{}},session:{set:async()=>{}}},
    tabs:{create:async x=>calls.push({create:x}),update:async(id,x)=>calls.push({update:id,...x})},windows:{update:async(id,x)=>calls.push({window:id,...x})},contextMenus:{onClicked:event('context'),removeAll:cb=>cb(),create:()=>{}},scripting:{executeScript:async()=>[]}
  };
  await import('../extension/worker.js');
  await listeners.click();assert.match(calls[0].create.url,/dashboard.html$/);
  contexts=[{tabId:4,windowId:7}];await listeners.click();assert.equal(calls[1].update,4);assert.equal(calls[2].window,7);
  const sender={id:chrome.runtime.id,url:chrome.runtime.getURL('dashboard.html')};
  const request=msg=>new Promise(resolve=>listeners.message(msg,sender,resolve));
  let r=await request({type:'open-session',accountId:'a2',sessionId:'s0'});assert.equal(r.ok,true);assert.equal(calls.at(-1).native.profileId,state.accounts[1].profileId);assert.equal(calls.at(-1).native.url,state.sessions[0].url);
  const before=calls.length;r=await request({type:'open-session',accountId:'a1',sessionId:'s0'});assert.equal(r.ok,false);assert.equal(calls.length,before);
  state.accounts[0].mode='current';r=await request({type:'open-session',accountId:'a1',sessionId:'s1'});assert.equal(r.ok,true);assert.equal(calls.at(-1).create.url,state.sessions[1].url);
  let responded=false;assert.equal(listeners.message({type:'open-session'},{id:sender.id,url:'https://claude.ai/code'},()=>responded=true),undefined);assert.equal(responded,false);
});
