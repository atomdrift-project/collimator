#!/usr/bin/env python3
"""Wait for an authorized primary correction to reach the training replica."""
import argparse
from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import time

from collimator import data


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--db',default='postgres://hopper@localhost:5432/hopper')
    p.add_argument('--id',type=int,required=True)
    p.add_argument('--sha256',required=True)
    p.add_argument('--label',choices=['bad','good'],required=True)
    p.add_argument('--status',type=Path,required=True)
    args=p.parse_args()
    logging.basicConfig(level=logging.INFO,format='%(asctime)s %(levelname)s %(message)s')
    while True:
        with data._connect(args.db) as conn:
            row=conn.execute('SELECT sha256,label,path,label_source,canonical_sha256 FROM samples WHERE id=%s',(args.id,)).fetchone()
        if row is None or row[0]!=args.sha256:
            raise ValueError('Correction identity does not match the training database')
        ready=row[1]==args.label and row[3]=='triage'
        status={'status':'verified' if ready else 'waiting_for_replication','id':args.id,
                'sha256':row[0],'label':row[1],'path':row[2],'label_source':row[3],
                'canonical_sha256':row[4],'checked_at':datetime.now(timezone.utc).isoformat()}
        args.status.parent.mkdir(parents=True,exist_ok=True)
        temp=args.status.with_suffix('.tmp');temp.write_text(json.dumps(status,indent=2)+'\n');temp.replace(args.status)
        if ready:
            logging.info('Verified replicated correction for %s: %s',args.id,args.label)
            return
        logging.info('Waiting for corrected label on training replica: id=%s current=%s expected=%s',args.id,row[1],args.label)
        time.sleep(30)


if __name__=='__main__':main()
