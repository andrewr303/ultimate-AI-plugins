#!/usr/bin/env node
'use strict';
const fs=require('node:fs');
const path=require('node:path');
const {handle,frame,createDecoder}=require('./core.cjs');
let config;
try {config=JSON.parse(fs.readFileSync(path.join(__dirname,'config.json'),'utf8'));}catch{process.exit(1);}
// Chrome passes the initiating extension origin. The manifest and host both bind to it.
if(!/^[a-p]{32}$/.test(config.extensionId||'') || process.argv[2]!==`chrome-extension://${config.extensionId}/`) process.exit(1);
let chain=Promise.resolve();
const send=x=>process.stdout.write(frame(x));
const decoder=createDecoder(msg=>{chain=chain.then(async()=>{try{send(await handle(msg));}catch(e){send({ok:false,error:e.message});}});},e=>send({ok:false,error:e.message}));
process.stdin.on('data',chunk=>decoder.push(chunk));
process.stdin.on('end',()=>decoder.end());
process.stdout.on('error',()=>process.exit(1));
