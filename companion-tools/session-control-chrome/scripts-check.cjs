const fs=require('node:fs');const path=require('node:path');const cp=require('node:child_process');
function files(dir){return fs.readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?files(path.join(dir,e.name)):[path.join(dir,e.name)]);}
const source=files('extension').concat(files('mac-helper'));
for(const file of source.filter(f=>/\.(?:c?js)$/.test(f))){const r=cp.spawnSync(process.execPath,['--check',file],{encoding:'utf8'});if(r.status){process.stderr.write(r.stderr);process.exit(1);}}
const m=JSON.parse(fs.readFileSync('extension/manifest.json'));for(const file of [m.background.service_worker,...Object.values(m.icons),'dashboard.html','app.js','style.css'])if(!fs.existsSync(path.join('extension',file)))throw Error('Missing extension file: '+file);
if(m.host_permissions||m.content_scripts)throw Error('Unexpected background page access.');
if(/@import|https?:\/\//.test(fs.readFileSync('extension/style.css','utf8')))throw Error('Styles must load locally.');
for(const file of source.filter(f=>f.endsWith('.command'))){const r=cp.spawnSync('bash',['-n',file]);if(r.status)throw Error('Invalid shell script: '+file);}
console.log('JavaScript syntax, shell syntax, manifest assets, and local-only styles checked.');
