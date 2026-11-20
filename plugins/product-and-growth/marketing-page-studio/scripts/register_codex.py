#!/usr/bin/env python3
"""Copy this independently packaged plugin into a repo-local Codex marketplace.

Run after extracting a studio archive:
  python PLUGIN/scripts/register_codex.py --repo MY_REPO
The helper preserves existing marketplace entries, refuses conflicts, and never
installs the plugin or writes user-home state. Run the reported Codex commands
when you want to install it.
"""
from __future__ import annotations
import argparse
import json
import os
from pathlib import Path
import re
import shutil
import sys
import tempfile

ROOT=Path(__file__).resolve().parents[1]


def register(repo: Path, marketplace: str | None = None, dry_run: bool = False) -> dict:
    manifest_path=ROOT/'plugin.json'
    if not manifest_path.is_file():raise ValueError('Run the helper from a complete extracted plugin: missing plugin.json beside scripts/.')
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    name=manifest.get('name')
    if manifest.get('$schema')!='https://agent-plugins.org/schemas/1.0.0/plugin.schema.json' or not isinstance(name,str) or not re.fullmatch(r'[a-z0-9][a-z0-9.-]*',name):raise ValueError('Package has an invalid portable plugin identity.')
    repo=repo.resolve()
    if repo==ROOT or repo.is_relative_to(ROOT):raise ValueError('The destination repo must be outside the source plugin to avoid recursive copying.')
    target=repo/'plugins'/name
    catalog=repo/'.agents/plugins/marketplace.json'
    for path in (target,catalog):
        if not path.resolve().is_relative_to(repo):raise ValueError('Destination path escapes the repo through a symlink: '+str(path))
    if target.exists() or target.is_symlink():raise ValueError('Destination already exists; no files were overwritten: '+str(target))
    if catalog.exists():
        doc=json.loads(catalog.read_text(encoding='utf-8'))
        if not isinstance(doc,dict) or not isinstance(doc.get('plugins'),list) or not isinstance(doc.get('name'),str) or not doc['name'].strip():raise ValueError('Existing marketplace must be an object with name and plugins array; repair it before continuing.')
        if marketplace is not None and marketplace!=doc['name']:raise ValueError('Requested marketplace name differs from the existing catalog; existing identity was preserved.')
    else:
        doc={'name':marketplace or 'studio-local','plugins':[]}
    if any(isinstance(p,dict) and p.get('name')==name for p in doc['plugins']):raise ValueError('Marketplace already contains this plugin name; no entry was replaced: '+name)
    for p in ROOT.rglob('*'):
        if p.is_symlink():raise ValueError('Plugin contains a symlink; package regular files before registration: '+p.relative_to(ROOT).as_posix())
    entry={'name':name,'source':{'source':'local','path':'./plugins/'+name},'policy':{'installation':'AVAILABLE','authentication':'ON_INSTALL'},'category':'Productivity'}
    new_doc={**doc,'plugins':[ *doc['plugins'],entry]}
    result={'status':'planned' if dry_run else 'registered','plugin':name,'repo':str(repo),'copiedPlugin':str(target),'marketplacePath':str(catalog),'marketplaceName':doc['name'],'preservedEntries':len(doc['plugins']),'installed':False,'followupCommands':[['codex','plugin','marketplace','add',str(repo),'--json'],['codex','plugin','add',name+'@'+doc['name'],'--json']],'next':'Run followupCommands to install, then start a new Codex session. No existing user-home configuration was changed.'}
    if dry_run:return result
    target.parent.mkdir(parents=True,exist_ok=True)
    # Atomic reservation refuses an existing target, including one created concurrently.
    target.mkdir()
    try:
        shutil.copytree(ROOT,target,dirs_exist_ok=True,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache','.git'))
        catalog.parent.mkdir(parents=True,exist_ok=True)
        fd,tmp=tempfile.mkstemp(prefix='marketplace-',suffix='.json',dir=catalog.parent)
        try:
            with os.fdopen(fd,'w',encoding='utf-8') as stream:json.dump(new_doc,stream,indent=2);stream.write('\n')
            os.replace(tmp,catalog)
        finally:
            if Path(tmp).exists():Path(tmp).unlink()
    except Exception:
        shutil.rmtree(target)
        raise
    return result


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--repo',required=True,type=Path)
    parser.add_argument('--marketplace',help='Default studio-local for a new catalog; an existing catalog retains its name.')
    parser.add_argument('--dry-run',action='store_true')
    args=parser.parse_args(argv)
    try:report=register(args.repo,args.marketplace,args.dry_run)
    except (OSError,ValueError) as exc:
        print(json.dumps({'status':'error','message':str(exc)}));return 1
    print(json.dumps(report,indent=2));return 0

if __name__=='__main__':raise SystemExit(main())
