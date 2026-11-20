'use strict';
const fs = require('node:fs');
const path = require('node:path');
const os = require('node:os');
const { execFile } = require('node:child_process');
const HOST = 'com.sessioncontrol.chrome';
const UUID = /^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i;
function cloudUrl(value) {
  if(typeof value !== 'string' || value.length>2048) throw Error('Invalid Claude Code URL.');
  let u;try {u=new URL(value);}catch {throw Error('Invalid Claude Code URL.');}
  if(u.protocol!=='https:' || u.hostname!=='claude.ai' || u.port || u.username || u.password || !/^\/code(?:\/[A-Za-z0-9_-]+)*\/?$/.test(u.pathname) || u.search || u.hash) throw Error('Only canonical https://claude.ai/code URLs may be opened.');
  return `https://claude.ai${u.pathname.replace(/\/$/,'')}`;
}
function launchPlan(message,{platform=process.platform,home=os.homedir(),exists=fs.existsSync}={}) {
  if(platform!=='darwin') throw Error('The account profile helper requires macOS.');
  if(!message || message.type!=='open' || !UUID.test(message.profileId||'')) throw Error('Invalid account profile ID.');
  const url=cloudUrl(message.url);
  const app=['/Applications/Google Chrome.app',path.join(home,'Applications/Google Chrome.app')].find(exists);
  if(!app) throw Error('Install Google Chrome in Applications, then try again.');
  const profile=path.join(home,'Library/Application Support/SessionControlChrome/Profiles',message.profileId.toLowerCase());
  const user=os.userInfo().username;
  return {command:'/usr/bin/open',args:['-n','-a',app,'--args',`--user-data-dir=${profile}`,'--profile-directory=Default','--no-first-run','--no-default-browser-check',url],profile,options:{timeout:15000,maxBuffer:16384,env:{HOME:home,USER:user,LOGNAME:user,PATH:'/usr/bin:/bin:/usr/sbin:/sbin',TMPDIR:os.tmpdir()}}};
}
async function handle(message,options={}) {
  const platform=options.platform || process.platform;
  if(message?.type==='ping') return platform==='darwin'?{ok:true,version:'0.5.0',platform:'macOS'}:{ok:false,error:'The account profile helper requires macOS.'};
  const plan=launchPlan(message,options);
  const mkdir=options.mkdir || (p=>fs.mkdirSync(p,{recursive:true,mode:0o700}));
  // No cookie or credential reads. Only this app's dedicated profile directory is created.
  mkdir(plan.profile);
  const run=options.run || ((cmd,args,opts)=>new Promise((resolve,reject)=>execFile(cmd,args,opts,e=>e?reject(Error('Chrome could not be opened. Check that Google Chrome is installed and try again.')):resolve())));
  await run(plan.command,plan.args,plan.options);
  return {ok:true,opened:true};
}
function frame(value) {
  const body=Buffer.from(JSON.stringify(value),'utf8'),header=Buffer.alloc(4);header.writeUInt32LE(body.length);return Buffer.concat([header,body]);
}
function createDecoder(onMessage,onError) {
  let buffer=Buffer.alloc(0),dead=false;
  return {push(chunk){
    if(dead)return;
    buffer=Buffer.concat([buffer,chunk]);
    while(buffer.length>=4){
      const n=buffer.readUInt32LE(0);
      if(n<2 || n>65536){dead=true;buffer=Buffer.alloc(0);onError(Error('Native message exceeds the allowed size.'));return;}
      if(buffer.length<4+n)return;
      const body=buffer.subarray(4,4+n);buffer=buffer.subarray(4+n);
      try {onMessage(JSON.parse(body.toString('utf8')));}catch{onError(Error('Invalid native JSON message.'));}
    }
  },end(){if(buffer.length&&!dead)onError(Error('Incomplete native message.'));}};
}
module.exports={HOST,cloudUrl,launchPlan,handle,frame,createDecoder};
