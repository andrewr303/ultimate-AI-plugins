const {test}=require('node:test');
const assert=require('node:assert/strict');
const fs=require('node:fs');const os=require('node:os');const path=require('node:path');
const {spawnSync}=require('node:child_process');
const {launchPlan,handle,frame,createDecoder}=require('../mac-helper/core.cjs');
const {install}=require('../mac-helper/install.cjs');
const id='0b336235-3358-4cb4-9500-123456789abc';
const options={platform:'darwin',home:'/Users/test user',exists:p=>p==='/Applications/Google Chrome.app'};
test('each profile is confined to a dedicated directory and launch arguments are not shell commands',()=>{
  const plan=launchPlan({type:'open',profileId:id,url:'https://claude.ai/code/session_abc'},options);
  assert.equal(plan.command,'/usr/bin/open');assert.equal(plan.profile,`/Users/test user/Library/Application Support/SessionControlChrome/Profiles/${id}`);
  assert.ok(plan.args.includes(`--user-data-dir=${plan.profile}`));assert.equal(plan.args.at(-1),'https://claude.ai/code/session_abc');
  assert.equal(plan.options.env.HOME,options.home);assert.deepEqual(Object.keys(plan.options.env).sort(),['HOME','LOGNAME','PATH','TMPDIR','USER']);
  for(const profileId of ['../../Default',id+';echo stolen','default','-n'])assert.throws(()=>launchPlan({type:'open',profileId,url:'https://claude.ai/code'},options));
});
test('invalid URLs fail before creating profiles or starting a process',async()=>{
  let touched=false;
  for(const url of ['file:///etc/passwd','https://evil.test/code','https://claude.ai/code?x=1','https://claude.ai/code#x','https://claude.ai/code/../../settings'])await assert.rejects(()=>handle({type:'open',profileId:id,url},{...options,mkdir:()=>{touched=true;},run:()=>{touched=true;}}));
  assert.equal(touched,false);
});
test('valid account opens once through an injected macOS launcher, without launching a real browser',async()=>{
  const calls=[];
  assert.deepEqual(await handle({type:'open',profileId:id,url:'https://claude.ai/code/s1'},{...options,mkdir:p=>calls.push(['mkdir',p]),run:async(c,a)=>calls.push([c,a])}),{ok:true,opened:true});
  assert.equal(calls.length,2);assert.equal(calls[1][0],'/usr/bin/open');
  await assert.rejects(()=>handle({type:'open',profileId:id,url:'https://claude.ai/code'},{...options,exists:()=>false}),/Install Google Chrome/);
  assert.equal((await handle({type:'ping'},{platform:'linux'})).ok,false);
});
test('native framing supports split headers, multiple messages, and rejects malformed frames',()=>{
  const messages=[],errors=[];const d=createDecoder(x=>messages.push(x),e=>errors.push(e.message));
  const data=Buffer.concat([frame({type:'ping'}),frame({type:'open',profileId:id})]);
  for(let i=0;i<data.length;i+=3)d.push(data.subarray(i,i+3));d.end();assert.equal(messages.length,2);assert.equal(errors.length,0);
  const bad=Buffer.alloc(4);bad.writeUInt32LE(65537);d.push(bad);assert.match(errors[0],/size/);
  const partial=createDecoder(()=>{},e=>errors.push(e.message));partial.push(Buffer.from([1,0]));partial.end();assert.match(errors.at(-1),/Incomplete/);
});
test('Mac installer binds one extension origin and preserves existing profile data',()=>{
  const home=fs.mkdtempSync(path.join(os.tmpdir(),"sc install '$() "));
  try {
    const profile=path.join(home,'Library/Application Support/SessionControlChrome/Profiles/keep');fs.mkdirSync(profile,{recursive:true});fs.writeFileSync(path.join(profile,'sentinel'),'keep');
    const r=install({platform:'darwin',home,extensionId:'a'.repeat(32),node:process.execPath});
    const m=JSON.parse(fs.readFileSync(r.manifest));assert.deepEqual(m.allowed_origins,[`chrome-extension://${'a'.repeat(32)}/`]);
    assert.equal(spawnSync('sh',['-n',m.path]).status,0);assert.equal(fs.readFileSync(path.join(profile,'sentinel'),'utf8'),'keep');
    const ping=spawnSync(process.execPath,[path.join(r.root,'host.cjs'),m.allowed_origins[0]],{input:frame({type:'ping'})});
    const out=[];createDecoder(x=>out.push(x),e=>{throw e;}).push(ping.stdout);assert.equal(out[0].ok,process.platform==='darwin');
    const wrong=spawnSync(process.execPath,[path.join(r.root,'host.cjs'),`chrome-extension://${'b'.repeat(32)}/`],{input:frame({type:'ping'})});assert.equal(wrong.status,1);assert.equal(wrong.stdout.length,0);
    assert.throws(()=>install({platform:'darwin',home,extensionId:'../../bad'}),/extension ID/);
  } finally {fs.rmSync(home,{recursive:true,force:true});}
});
