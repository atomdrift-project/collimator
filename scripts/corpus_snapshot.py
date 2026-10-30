#!/usr/bin/env python3
"""Own a shared read-only database snapshot until stdin closes or command exits."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from collimator.corpus_snapshot import frozen_corpus, SNAPSHOT_ENV, DATABASE_ENV

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',required=True)
    p.add_argument('--serve',action='store_true')
    p.add_argument('command',nargs=argparse.REMAINDER)
    a=p.parse_args()
    with frozen_corpus(a.db):
        if a.serve:
            print(json.dumps({k:os.environ[k] for k in (SNAPSHOT_ENV,DATABASE_ENV) if k in os.environ}),flush=True)
            sys.stdin.buffer.read()
        else:
            cmd=a.command[1:] if a.command[:1]==['--'] else a.command
            if not cmd:p.error('provide a command or --serve')
            return subprocess.call(cmd)
    return 0
if __name__=='__main__':raise SystemExit(main())
