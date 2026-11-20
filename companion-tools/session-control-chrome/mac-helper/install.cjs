#!/usr/bin/env node
'use strict';
const fs=require('node:fs');
const os=require('node:os');
const path=require('node:path');
const {HOST}=require('./core.cjs');
function install({platform=process.platform,home=os.homedir(),extensionId,node=process.execPath,source=__dirname}={}) {
  if(platform!=='darwin')throw Error('Run this installer on your Mac.');
  if(Number(process.versions.node.split('.')[0])<22)throw Error('Install Node.js 22 or newer first.');
  if(!/^[a-p]{32}$/.test(extensionId||''))throw Error('Paste the 32-letter extension ID from Session Control → Settings.');
  if(!path.isAbsolute(node))throw Error('Node.js must have an absolute installation path.');
  const root=path.join(home,'Library/Application Support/SessionControlChrome/Bridge');
  const manifestDir=path.join(home,'Library/Application Support/Google/Chrome/NativeMessagingHosts');
  fs.mkdirSync(root,{recursive:true,mode:0o700});fs.mkdirSync(manifestDir,{recursive:true,mode:0o700});
  for(const file of ['core.cjs','host.cjs']) fs.writeFileSync(path.join(root,file),fs.readFileSync(path.join(source,file)),{mode:0o600});
  fs.writeFileSync(path.join(root,'config.json'),JSON.stringify({extensionId}),{mode:0o600});
  const quote=s=>"'"+s.replace(/'/g,"'\\''")+"'";
  const launcher=path.join(root,'launch-host');
  fs.writeFileSync(launcher,`#!/bin/sh\nexec ${quote(node)} ${quote(path.join(root,'host.cjs'))} "$@"\n`,{mode:0o700});
  fs.chmodSync(launcher,0o700);
  const manifest=path.join(manifestDir,HOST+'.json');
  fs.writeFileSync(manifest,JSON.stringify({name:HOST,description:'Session Control isolated Chrome account launcher',path:launcher,type:'stdio',allowed_origins:[`chrome-extension://${extensionId}/`]},null,2),{mode:0o600});
  return {root,manifest};
}
if(require.main===module){try{const r=install({extensionId:process.argv[2]});console.log(`Mac helper installed.\n\nReturn to Session Control → Settings → Check connection.\n\nInstalled manifest: ${r.manifest}\nNo existing browser profiles were changed.`);}catch(e){console.error(e.message);process.exitCode=1;}}
module.exports={install};
