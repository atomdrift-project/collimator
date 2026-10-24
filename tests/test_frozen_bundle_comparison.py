"""Paired evaluation freezes labels, routing, model inputs and row alignment."""
import json
from pathlib import Path
import sqlite3
import sys
from types import SimpleNamespace

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import compare_frozen_bundles as compare


def test_cohort_includes_test_and_only_pe_dev():
    buckets = np.array([0, 31, 32, 63, 64, 255])
    types = np.array(['zip', 'pe', 'pe', 'zip', 'pe', 'zip'])
    assert compare.cohort_mask(buckets, types).tolist() == [True, True, True, False, False, False]


def test_route_masks_follow_each_bundles_own_mapping():
    types = np.array(['ooxml', 'pe', 'vbs'])
    assert compare.route_mask('filegroups/documents', types, {'filetype_to_group': {}}).tolist() == [False]*3
    assert compare.route_mask('filegroups/documents', types, {'filetype_to_group': {'ooxml':'documents'}}).tolist() == [True,False,False]
    assert compare.route_mask('filetypes/pe', types, {}).tolist() == [False,True,False]


def test_unordered_results_align_and_missing_or_duplicate_rows_fail():
    expected = np.array([2,5,9])
    result = {'row_ids':np.array([9,2,5]), 'probs':np.array([.9,.2,.5])}
    assert compare.align_predictions(expected, result).tolist() == [.2,.5,.9]
    for ids in ([2,2,9], [2,5], [2,5,10]):
        with pytest.raises(ValueError, match='cohort row IDs'):
            compare.align_predictions(expected, {'row_ids':np.array(ids), 'probs':np.zeros(len(ids))})
    with pytest.raises(ValueError, match='non-finite probabilities'):
        compare.align_predictions(expected, {'row_ids':expected, 'probs':np.array([.2,np.nan,.9])})


def test_capture_freezes_source_labels_and_detects_mutated_or_added_inputs(tmp_path):
    source = tmp_path/'source'
    (source/'general').mkdir(parents=True)
    np.savez(source/'score_table.npz', row_ids=np.array([2,1,3]), labels=np.array([1,0,1]),
             file_types=np.array(['pe','zip','pe']), sha_bucket=np.array([32,0,255]))
    np.savez(source/'general/threshold_scores.npz', row_ids=np.array([1,2,3]),
             labels=np.array([0,1,1]), canonical_shas=np.array(['aa'*31+'00','bb'*31+'20','cc'*32]))
    (source/'config.json').write_text(json.dumps({'models':[{'route':'general'}], 'fit_partition':'dev',
        'levels':[{'level':25,'hostile':{'thresholds':{'general':.5}}}]}))
    (source/'route_policies.json').write_text('{}')
    (source/'general/model.txt').write_text('snapshot-only fixture')
    (source/'general/feature_spec.json').write_text('{}')
    db_path=tmp_path/'source.sqlite'
    with sqlite3.connect(db_path) as db:
        db.execute('CREATE TABLE samples (id INTEGER, cleave_result TEXT, formula TEXT, elements TEXT, '
                   'score INTEGER, mtime TEXT, label TEXT, sha256 TEXT)')
        db.executemany('INSERT INTO samples VALUES (?, ?, ?, ?, ?, ?, ?, ?)', [
            (1,'{}','','',0,'','good','aa'*32), (2,'{}','','',4,'','good','bb'*32)])
    capture=tmp_path/'capture'
    compare.capture(SimpleNamespace(capture=capture, source=source, bundle=['candidate='+str(source)], db=str(db_path)))
    manifest=compare.verify_capture(capture)
    assert manifest['rows']==2
    assert manifest['live_labels_differ_from_frozen']==[2]
    with np.load(capture/'cohort.npz') as cohort:
        assert cohort['row_ids'].tolist()==[1,2]
        assert cohort['labels'].tolist()==[0,1]
        assert cohort['scores'].tolist()==[0,4]
        score_table = {key:cohort[key] for key in ('row_ids','labels','file_types','sha_bucket')}
    results = tmp_path/'results'
    (results/'candidate').mkdir(parents=True)
    score_table.update(route_names=np.array(['general']), scores=np.array([[.8,.9]]))
    np.savez(results/'candidate/scores.npz', **score_table)
    compare.compare(SimpleNamespace(capture=capture, results=results, output=tmp_path/'comparison', level=25))
    report = json.loads((tmp_path/'comparison/comparison.json').read_text())
    assert report['bundles']['candidate']['test']['fp'] == 1
    assert report['bundles']['candidate']['test']['malware'] == 0
    assert report['pe_policy_crosscheck']['dev']['candidate']['candidate']['tp'] == 1
    score_table['labels'] = np.array([1,0])
    np.savez(results/'candidate/scores.npz', **score_table)
    with pytest.raises(ValueError, match='labels differs from frozen cohort'):
        compare.compare(SimpleNamespace(capture=capture, results=results, output=tmp_path/'invalid', level=25))
    # Later edits to the original model do not affect the frozen copy.
    (source/'general/model.txt').write_text('changed original')
    compare.verify_capture(capture)
    added=capture/'bundles/candidate/general/model.onnx'
    added.write_bytes(b'new higher-priority model')
    with pytest.raises(ValueError, match='file set changed'):
        compare.verify_capture(capture)
    added.unlink()
    (capture/'bundles/candidate/general/model.txt').write_text('changed snapshot')
    with pytest.raises(ValueError, match='captured input changed'):
        compare.verify_capture(capture)


def test_decisions_use_frozen_policies_and_general_fallback():
    table={'labels':np.array([1,0]), 'file_types':np.array(['pe','zip']),
           'route_names':np.array(['general','filetypes/pe']),
           'scores':np.array([[.9,.7],[.4,np.nan]])}
    config={'levels':[{'level':25,'hostile':{'thresholds':{'general':.6}}}]}
    policies={'routes':{'filetypes/pe':{'levels':[
        {'level':25,'hostile':{'best':{'thresholds':{'filetypes/pe':.5}}}}]}}}
    assert compare.decisions(table,config,policies,25).tolist()==[False,True]
    table['labels'][:]=[0,1]
    assert compare.decisions(table,config,policies,25).tolist()==[False,True]
