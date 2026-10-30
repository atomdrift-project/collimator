#!/usr/bin/env python3
"""Install configuration snapshots only; verify model artifacts stay identical."""
import argparse
import hashlib
from pathlib import Path
import shutil


def models(root):
    return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest()
            for p in root.rglob('*.onnx')}


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('source',type=Path);p.add_argument('target',type=Path);a=p.parse_args()
    before=models(a.target);copied=[];skipped=[]
    for source in a.source.rglob('*.json'):
        if not source.is_file():continue
        rel=source.relative_to(a.source)
        if source.name!='accepted_config.json' and rel.as_posix()!='.autocollie/promoted_baselines.json':
            raise ValueError(f'Unexpected file in metadata stage: {source}')
        target=a.target/rel
        if source.name=='accepted_config.json' and not target.parent.is_dir():skipped.append(str(rel));continue
        target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(source,target);copied.append(str(rel))
    assert before==models(a.target),'Model artifacts changed during metadata installation'
    print(f'Installed {len(copied)} metadata files; verified {len(before)} ONNX files unchanged; skipped absent routes: {skipped}')
if __name__=='__main__':main()
