#!/usr/bin/env python3
"""Portable local workflow tools. No API calls or uploads by default."""
from __future__ import annotations
import argparse, datetime, hashlib, importlib.util, json, os, platform, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
VERSION = '1.0.0'


def emit(value):
    print(json.dumps(value, indent=2, ensure_ascii=False))


def sha(path):
    h=hashlib.sha256()
    with open(path,'rb') as f:
        for block in iter(lambda:f.read(1024*1024),b''): h.update(block)
    return h.hexdigest()


def run_tool(rel, args):
    script=ROOT / rel
    if not script.is_file(): raise ValueError(f'Capability unavailable in this plugin: {rel}')
    return subprocess.call([sys.executable,str(script),*args])


def load(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def safe_path(base, value):
    p=Path(value)
    if p.is_absolute() or '..' in p.parts or '\\' in str(value) or re.match(r'^[A-Za-z][A-Za-z0-9+.-]*:',str(value)) or not str(value).strip(): raise ValueError(f'Expected a portable relative path: {value}')
    root=Path(base).resolve(); candidate=(root/p).resolve()
    if not candidate.is_relative_to(root): raise ValueError(f'Path escapes project: {value}')
    return candidate


def doctor(args):
    checks=[]
    def add(name,ok,detail,required=False): checks.append(dict(name=name,status='pass' if ok else ('fail' if required else 'unavailable'),required=required,detail=detail))
    add('python',sys.version_info >= (3,10),platform.python_version(),True)
    for module in ['jsonschema','playwright','PIL','yaml']:
        ok=importlib.util.find_spec(module) is not None
        add(module,ok,'installed' if ok else 'Install requirements.txt',module in ['jsonschema','playwright','PIL','yaml'])
    override=os.environ.get('STUDIO_BROWSER')
    browser=(override if Path(override).is_file() else None) if override else next((p for p in [shutil.which('chromium'),shutil.which('chromium-browser'),shutil.which('google-chrome'),shutil.which('msedge')] if p and Path(p).is_file()),None)
    if not browser and not override and importlib.util.find_spec('playwright'):
        from playwright.sync_api import sync_playwright
        with sync_playwright() as p:
            candidate=p.chromium.executable_path
            if Path(candidate).exists(): browser=candidate
    add('browser',bool(browser),browser or ('Configured STUDIO_BROWSER does not exist' if override else 'python -m playwright install chromium'),True)
    if browser and getattr(args,'launch',False):
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                b=p.chromium.launch(executable_path=browser,headless=True,args=['--no-sandbox']);page=b.new_page();page.set_content('<title>Studio doctor</title>');title=page.title();b.close()
            add('browser-launch',title=='Studio doctor',title,True)
        except Exception as e: add('browser-launch',False,str(e),True)
    is_video=(ROOT/'plugin.json').exists() and load(ROOT/'plugin.json')['name']=='product-demo-studio'
    for cmd in ['ffmpeg','ffprobe','node','codex','claude']:
        path=shutil.which(cmd);version=None
        if path:
            try:
                r=subprocess.run([path,'-version' if cmd in ['ffmpeg','ffprobe'] else '--version'],capture_output=True,text=True,timeout=8)
                version=(r.stdout or r.stderr).splitlines()[0][:180]
            except Exception: version='present; version query failed'
        available=bool(path)
        if cmd=='node' and version:
            match=re.search(r'v?(\d+)',version)
            available=bool(match and int(match.group(1))>=20)
            if not available:version+='; optional adapters require Node 20+'
        add(cmd,available,version or 'not on PATH',is_video and cmd in ['ffmpeg','ffprobe'])
    fonts=[]
    if shutil.which('fc-list'):
        r=subprocess.run(['fc-list',':','family'],capture_output=True,text=True,timeout=8)
        fonts=sorted(set(r.stdout.splitlines()))[:12]
    elif platform.system()=='Windows':
        fonts=[p.name for p in (Path(os.environ.get('WINDIR','C:/Windows'))/'Fonts').glob('*.ttf')][:12]
    add('fonts',bool(fonts),fonts or 'Browser system font fallback; verify text metrics')
    disk=shutil.disk_usage(Path(args.path).resolve())
    add('disk',disk.free >= 1024**3,dict(freeBytes=disk.free,recommendation='At least 1 GiB for preview; budget several GiB for final frames'),True)
    # Presence only: never print tokens, values or configuration files.
    checks.append(dict(name='optional-services',status='info',required=False,detail={n:bool(os.environ.get(n)) for n in ['OPENAI_API_KEY','ELEVENLABS_API_KEY']}))
    emit(dict(pluginRoot=str(ROOT),version=VERSION,platform=platform.system(),checks=checks,passed=not any(c['required'] and c['status']=='fail' for c in checks)))
    return int(any(c['required'] and c['status']=='fail' for c in checks))


def discover(args):
    out=Path(args.output).resolve();out.mkdir(parents=True,exist_ok=True)
    source=args.source;files=[];tokens={};notes=[];title='Unspecified product';revision='unversioned';source_type='repository'
    if re.match(r'^https?://',source):
        if not args.allow_network: raise ValueError('URL discovery requires --allow-network; it fetches this source only and never uploads local files')
        import urllib.request,urllib.parse
        req=urllib.request.Request(source,headers={'User-Agent':'StudioContext/1.0'})
        with urllib.request.urlopen(req,timeout=20) as response:
            html=response.read(2*1024*1024).decode('utf-8',errors='replace')
            final_url=response.url
        match=re.search(r'<title[^>]*>(.*?)</title>',html,re.S|re.I)
        if match: title=re.sub('<[^>]+>','',match.group(1)).strip()[:150]
        snapshot=out/'public-source.html';snapshot.write_text(html,encoding='utf-8')
        files=[{'path':'public-source.html','sha256':sha(snapshot),'bytes':snapshot.stat().st_size}]
        revision=files[0]['sha256'];source_type='public-website';notes.append('Read public HTML only; browser behavior and product claims still require verification.')
        notes.append('Fetched URL: '+final_url)
        css=html
    else:
        src=Path(source).resolve()
        if not src.exists(): raise ValueError('Source does not exist: '+source)
        if src.is_file():
            files=[{'path':src.name,'sha256':sha(src),'bytes':src.stat().st_size}];title=src.stem;css='';source_type='supplied-file'
            notes.append('Supplied visual/document requires human product interpretation; no features inferred from its filename.')
        else:
            title=src.name;css='';ignored={'.git','node_modules','.venv','venv','__pycache__','dist','.next','coverage'}
            permitted={'.md','.json','.css','.html','.tsx','.jsx','.ts','.js','.py','.vue','.svelte'}
            for folder,dirs,names in os.walk(src):
                dirs[:]=[d for d in dirs if d not in ignored and not d.startswith('.') and (Path(folder)/d).resolve()!=out]
                for name in sorted(names):
                    path=Path(folder)/name;rel=path.relative_to(src)
                    if path.is_symlink() or name.startswith('.') or path.suffix not in permitted or any(s in name.lower() for s in ['secret','credential','lock','private']): continue
                    if path.stat().st_size>1024*1024: continue
                    files.append({'path':rel.as_posix(),'sha256':sha(path),'bytes':path.stat().st_size})
                    if path.suffix in ['.css','.html'] and len(css)<1024*1024: css+='\n'+path.read_text(encoding='utf-8',errors='replace')
                    if len(files)>=500: break
                if len(files)>=500: notes.append('Inventory bounded at 500 relevant files.');break
            package=src/'package.json'
            if package.is_file() and not package.is_symlink():
                try:title=load(package).get('name',title)
                except ValueError:notes.append('package.json could not be parsed.')
            if shutil.which('git'):
                r=subprocess.run(['git','-C',str(src),'rev-parse','HEAD'],capture_output=True,text=True)
                if r.returncode==0: revision=r.stdout.strip()
            notes.append('Read-only local inventory; private files are not uploaded. Manifest hashes represent the actual inspected files, including dirty working-tree content.')
        if revision=='unversioned': revision=hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest()
    for name,value in re.findall(r'(--[\w-]+)\s*:\s*([^;{}\n]+)',css):
        if len(tokens)<80: tokens[name]=value.strip()
    brief=dict(schemaVersion=VERSION,id='product-brief',product=dict(name=title,revision=revision),sourceType=source_type,audience='Needs product-specific assessment',problem='Needs product-specific assessment',primaryWorkflow='Verify in source or browser',demonstrableCapability='Select one supported workflow',shippedVsPlanned='Do not infer planned capabilities are shipped',conversionAction='Needs product-specific CTA',assumptions=notes,evidenceStatus='Inventory collected; claims have not been verified')
    inventory=dict(schemaVersion=VERSION,id='discovery',files=files,brandTokens=tokens)
    (out/'product-brief.json').write_text(json.dumps(brief,indent=2),encoding='utf-8')
    (out/'discovery.json').write_text(json.dumps(inventory,indent=2),encoding='utf-8')
    evidence=dict(schemaVersion=VERSION,id='product-evidence',product=dict(name=title,revision=revision),claims=[])
    (out/'product-evidence.draft.json').write_text(json.dumps(evidence,indent=2),encoding='utf-8')
    emit(dict(status='context-collected',output=str(out),files=len(files),revision=revision,claimsVerified=0,next='Read the product brief, inspect behavior, and add sources and allowed uses to claims before creative production.'))
    return 0


def init(args):
    dest=Path(args.output).resolve()
    if dest.exists() and any(dest.iterdir()): raise ValueError('Output must be empty; choose a new project directory')
    src=ROOT/'examples'/'tandem'
    if not src.is_dir(): raise ValueError('This package has no bundled Tandem example')
    shutil.copytree(src,dest,dirs_exist_ok=True)
    if args.source:
        discover(argparse.Namespace(source=args.source,output=str(dest/'foundation'),allow_network=False))
    emit(dict(status='created',path=str(dest),sampleData=True,next='Replace synthetic identity with verified product evidence; see the entry skill.'))
    return 0


def index(args):
    records=[]
    for path in sorted((ROOT/'skills').glob('*/SKILL.md')):
        text=path.read_text(encoding='utf-8');name=path.parent.name
        desc=re.search(r'^description:\s*(.+)$',text,re.M)
        records.append(dict(kind='skill',name=name,path=path.relative_to(ROOT).as_posix(),description=desc.group(1).strip('"\'') if desc else ''))
    idx=ROOT/'references'/'index.json'
    if idx.is_file():
        data=load(idx)
        records.extend(data if isinstance(data,list) else data.get('resources',[]))
    if args.query: records=[r for r in records if args.query.lower() in json.dumps(r).lower()]
    emit(records);return 0


def handoff(args):
    source=Path(args.from_dir).resolve();dest=Path(args.output).resolve()
    if not source.is_dir(): raise ValueError('Handoff source must be a directory')
    if source==dest or dest.is_relative_to(source): raise ValueError('Handoff output must be outside its input tree')
    if dest.exists() and any(dest.iterdir()): raise ValueError('Handoff output must be empty')
    names={'brand.json':'brand','product-evidence.json':'product-evidence','capture-manifest.json':'capture-manifest','campaign-brief.json':'campaign-brief','asset-manifest.json':'asset-manifest','export-variants.json':'export-variants','experiment-manifest.json':'experiment-manifest'}
    docs={};assets={}
    for filename,schema in names.items():
        path=source/filename
        if not path.is_file(): continue
        if path.is_symlink(): raise ValueError('Handoff manifests must be regular local files: '+filename)
        result=subprocess.run([sys.executable,str(ROOT/'contracts'/'validate.py'),'--schema',schema,'--input',str(path),'--root',str(source)],capture_output=True,text=True)
        if result.returncode: raise ValueError(f'Invalid {filename}: {result.stdout or result.stderr}')
        docs[filename]=path
        obj=load(path)
        def walk(value):
            if isinstance(value,dict):
                local=value.get('path')
                if isinstance(local,str):
                    resolved=safe_path(source,local)
                    if not resolved.is_file(): raise ValueError('Missing handoff asset: '+local)
                    if value.get('sha256') and sha(resolved)!=value['sha256']: raise ValueError('Asset hash mismatch: '+local)
                    if any(x.startswith('.') for x in Path(local).parts): raise ValueError('Hidden assets cannot be handed off')
                    assets[local]=resolved
                for key,v in value.items():
                    if key.endswith('Path') and isinstance(v,str):
                        resolved=safe_path(source,v)
                        if not resolved.is_file(): raise ValueError('Missing handoff reference: '+v)
                        assets[v]=resolved
                    elif key!='path':walk(v)
            elif isinstance(value,list):
                for v in value: walk(v)
        walk(obj)
    if not docs: raise ValueError('No supported handoff documents found')
    dest.mkdir(parents=True,exist_ok=True)
    for rel,path in {**{n:p for n,p in docs.items()},**assets}.items():
        target=safe_path(dest,rel);target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(path,target)
    report={'schemaVersion':VERSION,'id':'handoff-receipt','files':[{'path':p.relative_to(dest).as_posix(),'sha256':sha(p)} for p in sorted(dest.rglob('*')) if p.is_file()]}
    (dest/'handoff-receipt.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    emit(dict(status='copied',documents=list(docs),assets=len(assets),output=str(dest)));return 0


def campaign(args):
    brief_path=Path(args.brief).resolve();brief=load(brief_path)
    result=subprocess.run([sys.executable,str(ROOT/'contracts'/'validate.py'),'--schema','campaign-brief','--input',str(brief_path),'--root',str(brief_path.parent),'--use','ads'],capture_output=True,text=True)
    if result.returncode: raise ValueError('Invalid campaign brief: '+(result.stdout or result.stderr))
    n=args.hooks; b=args.bodies;ratios=args.ratios.split(',')
    if not (1<=n<=3 and 1<=b<=2) or any(r not in ['9:16','16:9','1:1','4:5'] for r in ratios): raise ValueError('Use 1–3 hooks, 1–2 bodies and ratios 9:16,16:9,1:1,4:5')
    if len(set(ratios))!=len(ratios): raise ValueError('Ratios must be unique')
    if not 1<=args.max_variants<=36: raise ValueError('--max-variants must be 1–36')
    if n*b*len(ratios)>args.max_variants: raise ValueError('Matrix exceeds --max-variants; reduce axes or explicitly raise this cap')
    out=Path(args.output).resolve()
    hook_defs=[('problem',brief['problem'],'Problem recognition establishes relevance'),('workflow',brief['productAction'],'Immediate action creates curiosity'),('outcome',brief['promise'],'Outcome-first opening establishes value')]
    hooks=[dict(id=kind,text=txt,angle=kind,hypothesis=hypothesis) for kind,txt,hypothesis in hook_defs[:n]]
    bodies=[dict(id=body,approach=approach,proof=brief['productAction'],claims=brief['claims']) for body,approach in [('workflow','Direct workflow proof'),('before-after','Show before and settled result')][:b]]
    placements={'9:16':'vertical-short','16:9':'landscape','1:1':'square-feed','4:5':'portrait-feed'}
    experiments=[]
    for hook in hooks:
        for body in bodies:
            for ratio in ratios:
                exp=dict(id=f"{hook['id']}-{body['id']}-{ratio.replace(':','x')}",hookId=hook['id'],bodyId=body['id'],audience=brief['audience'],awareness=brief['awareness'],painOrOutcome=brief['problem'],cta=brief['cta'],placement=placements[ratio],aspectRatio=ratio,duration=12,variableTested='hook' if body['id']=='workflow' else 'body',hypothesis=hook['hypothesis']+'; compare within the same body and placement to isolate hook, or the same hook and placement to isolate body.',status='planned')
                if brief.get('offer'):exp['offer']=brief['offer']
                experiments.append(exp)
    result=dict(schemaVersion=VERSION,id='campaign-experiments',productRevision=brief['productRevision'],campaignId=brief['id'],hooks=hooks,bodies=bodies,experiments=experiments,previewFirst=True)
    spec=importlib.util.spec_from_file_location('_studio_contracts',ROOT/'contracts'/'validate.py')
    validator=importlib.util.module_from_spec(spec);spec.loader.exec_module(validator)
    report=validator.validate('experiment-manifest',result)
    if not report['ok']: raise ValueError('Generated campaign is invalid. Supply distinct product angles or request fewer hooks: '+json.dumps(report['errors']))
    out.mkdir(parents=True,exist_ok=True)
    (out/'experiment-manifest.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
    emit(dict(status='planned',variants=len(experiments),output=str(out/'experiment-manifest.json'),note='Hooks use supplied brief text and are proposals; evaluate evidence and preview before full rendering. Cross-aspect versions recompose one hypothesis.'));return 0


def package_check(args):
    root=Path(args.root).resolve() if args.root else ROOT
    errors=[];checks=[]
    manifest=root/'plugin.json'
    try:
        data=load(manifest)
        if data.get('$schema')!='https://agent-plugins.org/schemas/1.0.0/plugin.schema.json': errors.append('Wrong portable schema identifier')
        from jsonschema import Draft202012Validator
        schema=load(root/'contracts'/'host'/'portable-plugin.schema.json')
        errors += ['plugin.json: '+e.message for e in Draft202012Validator(schema).iter_errors(data)]
        if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[a-zA-Z0-9.-]+)?',data.get('version','')):errors.append('version must be SemVer')
        cc=load(root/'.claude-plugin'/'plugin.json')
        if cc.get('name')!=data.get('name') or cc.get('version')!=data.get('version'): errors.append('Claude/portable identity mismatch')
    except Exception as e: errors.append('Manifest check: '+str(e))
    names=[]
    try: import yaml
    except ImportError: errors.append('PyYAML unavailable: install requirements.txt');yaml=None
    for skill in sorted((root/'skills').glob('*/SKILL.md')):
        text=skill.read_text(encoding='utf-8')
        try:
            if not text.startswith('---\n'): raise ValueError('Missing frontmatter')
            meta=yaml.safe_load(text.split('---',2)[1]) if yaml else {}
            if not isinstance(meta,dict) or not all(isinstance(meta.get(k),str) and meta[k].strip() for k in ['name','description']):raise ValueError('Nonblank name and description required')
            names.append(meta['name'])
            if len(text.encode())>1024*1024:raise ValueError('Skill exceeds 1 MiB')
            agent=skill.parent/'agents'/'openai.yaml'
            if agent.exists() and yaml and not isinstance(yaml.safe_load(agent.read_text()),dict):raise ValueError('openai.yaml must be an object')
        except Exception as e:errors.append(f'{skill.relative_to(root)}: {e}')
    if not names:errors.append('No usable skills')
    if len(names)!=len(set(names)):errors.append('Duplicate skill names')
    # Markdown links are actual references; inline code snippets are examples and handled by executable tests.
    for path in root.rglob('*.md'):
        if any(part in ['node_modules','.git','__pycache__'] for part in path.parts):continue
        text=path.read_text(encoding='utf-8')
        for link in re.findall(r'(?<!!)\[[^\]]+\]\(([^\s)]+)(?:\s+[^)]*)?\)',text):
            if re.match(r'^[a-z]+:',link) or link.startswith('#') or '<' in link:continue
            target=link.split('#')[0]
            if target and not (path.parent/target).exists():errors.append(f'{path.relative_to(root)} broken link: {link}')
        if re.search(r'/workspace/(?:work|attachments)|/home/[A-Za-z0-9_-]+/|~/code/',text):errors.append(f'{path.relative_to(root)} contains development-specific path')
    for path in root.rglob('*'):
        if path.is_symlink():errors.append(f'Symlink not portable: {path.relative_to(root)}')
        if path.is_file() and path.name in ['.env','credentials.json']:errors.append(f'Sensitive filename: {path.relative_to(root)}')
    for needed in ['LICENSE','THIRD_PARTY_NOTICES.md','requirements.txt','contracts/validate.py','references/index.json']:
        if not (root/needed).is_file():errors.append('Missing '+needed)
    checks.extend(['portable manifest schema','Claude compatibility identity','skill frontmatter','markdown links','portable source paths','required license/resources'])
    emit(dict(passed=not errors,root=str(root),skills=len(names),checks=checks,errors=errors));return int(bool(errors))


def parser():
    p=argparse.ArgumentParser(description='Local production utilities; execute from any working directory. No uploads, deployment, or paid API calls.')
    sub=p.add_subparsers(dest='command',required=True)
    d=sub.add_parser('doctor',help='Check actual dependencies; --launch exercises Chromium');d.add_argument('--path',default='.');d.add_argument('--launch',action='store_true');d.set_defaults(func=doctor)
    d=sub.add_parser('discover',help='Inventory supplied local context; public URLs need explicit network flag');d.add_argument('--source',required=True);d.add_argument('--output',required=True);d.add_argument('--allow-network',action='store_true');d.set_defaults(func=discover)
    d=sub.add_parser('init',help='Copy runnable synthetic example into an empty project directory');d.add_argument('--output',required=True);d.add_argument('--source');d.set_defaults(func=init)
    d=sub.add_parser('validate',help='Validate a versioned production contract');d.add_argument('--schema',required=True);d.add_argument('--input',required=True);d.add_argument('--root');d.add_argument('--use',choices=['internal','website','video','ads'],default='internal');d.add_argument('--evidence');d.add_argument('--captures');d.add_argument('--check-files',action='store_true');d.set_defaults(func=lambda a:run_tool('contracts/validate.py',['--schema',a.schema,'--input',a.input,'--use',a.use]+(['--root',a.root] if a.root else [])+(['--evidence',a.evidence] if a.evidence else [])+(['--captures',a.captures] if a.captures else [])+(['--check-files'] if a.check_files else [])))
    d=sub.add_parser('index',help='Find a focused skill or reference');d.add_argument('--query',default='');d.set_defaults(func=index)
    d=sub.add_parser('handoff',help='Validate and copy referenced handoff documents/assets with hashes');d.add_argument('--from-dir',required=True);d.add_argument('--output',required=True);d.set_defaults(func=handoff)
    d=sub.add_parser('campaign',help='Build a bounded campaign matrix from supplied brief text');d.add_argument('--brief',required=True);d.add_argument('--output',required=True);d.add_argument('--hooks',type=int,default=3);d.add_argument('--bodies',type=int,default=2);d.add_argument('--ratios',default='9:16,16:9');d.add_argument('--max-variants',type=int,default=12);d.set_defaults(func=campaign)
    d=sub.add_parser('package-check',help='Validate package manifests, metadata, paths and references');d.add_argument('--root');d.set_defaults(func=package_check)
    for name,script in [('web','scripts/web.py'),('capture','scripts/capture.py'),('render','scripts/render.py'),('media','scripts/media.py')]:
        d=sub.add_parser(name,help=f'Pass arguments to {script}',add_help=False);d.add_argument('args',nargs=argparse.REMAINDER);d.set_defaults(func=lambda a,s=script:run_tool(s,a.args))
    return p


def main():
    try:
        if len(sys.argv)>1 and sys.argv[1] in ['web','capture','render','media']:
            return run_tool({'web':'scripts/web.py','capture':'scripts/capture.py','render':'scripts/render.py','media':'scripts/media.py'}[sys.argv[1]],sys.argv[2:])
        args=parser().parse_args();return args.func(args)
    except (ValueError,OSError,KeyError) as e:
        emit(dict(status='error',error=str(e)));return 2

if __name__=='__main__':raise SystemExit(main())
