#!/usr/bin/env python3
"""Matched regression diagnosis and bounded optimization; no automatic deployment.

Both model generations see the same fetched report bytes. Candidate selection
never sees locked test rows. Historical model scores on training rows cannot
participate in selection. Small routes reserve all development rows for review.
"""
from __future__ import annotations

import argparse
import concurrent.futures as futures
from dataclasses import fields
import hashlib
import itertools
import json
import logging
import multiprocessing
import os
from pathlib import Path
import shutil
from types import SimpleNamespace

import lightgbm as lgb
import numpy as np
from scipy import sparse

import azoth_portable_stability as study
import azoth_specialist_tuneup as tune
import tune_regressed_models as initial
from azoth_specialist_suite import _temporary_feature_env
from collimator import data, features, model, export, train
from collimator.fit_resources import estimate_fit_gb, fit_reservation

LOG = logging.getLogger('regression_recovery')
GRID = {
    'control': {},
    'cap2': {'max_delta_step': 2.},
    'cap5_weight025_no_hnm': {'max_delta_step': 5., 'scale_pos_weight_mult': .25,
                             'hard_negative_fraction': 0.},
    'finer_regularized': {'min_child_samples': 10, 'min_child_weight': 1.,
                         'num_leaves': 32, 'max_depth': 8, 'reg_lambda': 5.,
                         'scale_pos_weight_mult': .25, 'hard_negative_fraction': 0.,
                         'max_delta_step': 2.},
}
LAYOUT_ABLATIONS = {'filetypes/go', 'filetypes/kotlin', 'filegroups/portable'}


def inventory(comparison, source, include_ap=False):
    routes = {}
    for row in comparison['models']:
        ap_drop = (include_ap and row.get('old_ap') is not None and row.get('new_ap') is not None
                   and row['new_ap'] < row['old_ap'])
        if row['delta'] < 0 or ap_drop:
            routes.setdefault(row['route'], set()).add(row['ft'])
    for row in comparison['routed']:
        route = 'filetypes/' + row['ft']
        if row['delta'] < 0 and (source / route / 'models').is_dir():
            routes.setdefault(route, set()).add(row['ft'])
    return {route: sorted(types) for route, types in sorted(routes.items())}


def filetype_profile(y, probability, filetypes, targets):
    result = study.metrics(y, probability)
    slices = {str(ft): study.metrics(y[filetypes == ft], probability[filetypes == ft])
              for ft in np.unique(filetypes)}
    result['by_filetype'] = slices
    supported = [slices[ft] for ft in targets if ft in slices and slices[ft]['malware']]
    total = sum(v['malware'] for v in supported)
    result['target_recall_1fp'] = (sum(v['at_fp']['1']['tp'] for v in supported) / total
                                  if total else None)
    result['target_malware'] = total
    result['target_ap'] = sum(v['ap'] * v['malware'] for v in supported) / total if total else None
    return result


def choose(records, reference, objective='recall', protect_filetypes=False):
    eligible = [r for r in records if r['selection']['target_recall_1fp'] is not None
                and r['selection']['ap'] is not None
                and r['selection']['ap'] >= (reference['selection']['ap'] or 0) - .02]
    if protect_filetypes:
        eligible = [r for r in eligible if all(
            r['selection']['by_filetype'][ft]['at_fp']['1']['tp'] >= old['at_fp']['1']['tp']
            for ft, old in reference['selection']['by_filetype'].items() if old['malware'])]
    if not eligible:
        return reference
    primary = 'target_ap' if objective == 'ap' else 'target_recall_1fp'
    return max(eligible, key=lambda r: (r['selection'][primary], r['selection']['target_recall_1fp'], r['selection']['ap']))


def memberships(seeds, subsets=False):
    result=[tuple(seeds)]
    if subsets:
        result += [s for size in range(1,len(seeds)) for s in itertools.combinations(seeds,size)]
    return result


def sampling_fraction(route, benchmark, cap):
    # Whole canonical groups, independent of selection/assessment assignment.
    if cap <= 0:
        raise ValueError('Training cap must be positive')
    return min(1., cap / max(1, benchmark['train_rows']))


def search_grid(path):
    grid = json.loads(path.read_text()) if path else GRID
    if not isinstance(grid, dict) or grid.get('control') != {}:
        raise ValueError('Search grid must include an unchanged control')
    for name, overrides in grid.items():
        if not name or any(c not in 'abcdefghijklmnopqrstuvwxyz0123456789_' for c in name):
            raise ValueError(f'Invalid variant name: {name!r}')
        if not isinstance(overrides, dict):
            raise ValueError(f'Variant {name} must contain configuration overrides')
        unknown=set(overrides)-{field.name for field in fields(train.TrainConfig)}
        if unknown:
            raise ValueError(f'Variant {name} cannot be replayed by TrainConfig: {sorted(unknown)}')
    return grid


def metadata(args, route, benchmark, fraction):
    rows = []
    query = ('SELECT id, sha256, canonical_sha256, label, score, file_type FROM samples WHERE '
             + data.LABELED_WHERE + ' AND id <= %s')
    params = [args.max_id]
    if route != 'general':
        query += ' AND file_type = ANY(%s)'
        params.append(benchmark['file_types'])
    # The stable sampling expression has a database index, avoiding random LIMIT
    # and retaining duplicate groups together. Development remains unsampled
    # except for the general model's deliberately bounded research screen.
    if route == 'general':
        query += " AND substr(md5(lower(COALESCE(NULLIF(canonical_sha256,''),sha256))),1,8) <= %s"
        params.append(f'{int(fraction * (2**32 - 1)):08x}')
    query += ' ORDER BY id'
    with data._connect(args.db, repeatable_read=True) as conn:
        with conn.cursor(name='recovery_metadata') as cur:
            cur.itersize = 10000
            cur.execute(query, params)
            for rid, sha, canonical, label, score, ft in cur:
                key = canonical or sha
                partition = data.partition_of(key)
                if partition == 'test':
                    continue
                y = int(label == 'bad')
                if partition == 'train':
                    if y and (score or 0) < benchmark['min_malware_training_score']:
                        continue
                    if route != 'general' and int(hashlib.md5(key.lower().encode()).hexdigest()[:8], 16) / 2**32 > fraction:
                        continue
                bucket = study.split_bucket(key)
                rows.append((int(rid), y, partition == 'dev', bucket, data.route_filetype(ft), int(score or 0)))
    return rows


_SPECS = None
_DB = None
_ENVS = {}
_LAYOUT_IDENTITIES = {}


def init_worker(db, paths, envs):
    global _SPECS, _DB, _ENVS, _LAYOUT_IDENTITIES
    _DB = db
    _ENVS = envs
    _SPECS = {name: features.FeatureSpec.load(path) for name, path in paths.items()}
    _LAYOUT_IDENTITIES = {name:(hashlib.sha256(Path(path).read_bytes()).hexdigest(),
                                json.dumps(envs.get(name,{}),sort_keys=True))
                          for name,path in paths.items()}


def paired_batch(rows):
    reports = data.fetch_cleave_results(_DB, [r[0] for r in rows],
                                      evaluation_labels={r[0]: r[1] for r in rows})
    kept = [r for r in rows if r[0] in reports and features._coerce_report(reports[r[0]]['cleave_result']) is not None]
    batch = [(reports[r[0]], r[1], False) for r in kept]
    matrices = {};extracted={}
    for name, spec in _SPECS.items():
        identity=_LAYOUT_IDENTITIES.get(name,name)
        if identity in extracted:
            matrices[name]=extracted[identity]
            continue
        with _temporary_feature_env(_ENVS.get(name, {})):
            rr, cc, vv, yy, *_ = features._extract_partitioned_batch_worker((0, 0, batch, spec))
        if len(yy) != len(kept):
            raise ValueError('Layout-dependent row loss')
        matrices[name] = sparse.csr_matrix((np.asarray(vv, np.float32), (rr, cc)),
                                           shape=(len(kept), spec.total_features))
        extracted[identity]=matrices[name]
    return kept, matrices, b''.join(reports[r[0]]['evaluation_digest'] for r in kept)


def checkpointed_batch(task):
    """Persist each matched extraction atomically; reuse only identical inputs."""
    directory,index,rows=task
    root=Path(directory)/f'{index:08d}'
    marker=root/'complete.json'
    requested=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
    if marker.exists():
        record=json.loads(marker.read_text())
        if record['requested_sha256']!=requested or set(record['matrices'])!=set(_SPECS):
            raise ValueError('Checkpointed extraction inputs changed: '+str(root))
        matrices={}
        for layout,digest in record['matrices'].items():
            path=root/(layout+'.npz')
            if initial.fingerprint(path)!=digest:
                raise ValueError('Checkpointed matrix changed: '+str(path))
            matrix=sparse.load_npz(path)
            if matrix.shape!=(len(record['kept']),_SPECS[layout].total_features):
                raise ValueError('Checkpointed matrix dimensions changed')
            matrices[layout]=matrix
        return record['kept'],matrices,bytes.fromhex(record['report_fingerprints'])
    kept,matrices,fingerprints=paired_batch(rows)
    root.mkdir(parents=True,exist_ok=True)
    hashes={}
    for layout,matrix in matrices.items():
        path=root/(layout+'.npz');temporary=root/(layout+'.tmp.npz')
        sparse.save_npz(temporary,matrix)
        temporary.replace(path)
        hashes[layout]=initial.fingerprint(path)
    study.write_json(marker,{'requested_sha256':requested,'kept':kept,
        'report_fingerprints':fingerprints.hex(),'matrices':hashes})
    return kept,matrices,fingerprints


def prepare(args, root, route, benchmark):
    if (root / 'prepared.json').exists():
        return
    fraction = sampling_fraction(route, benchmark, args.train_cap)
    cohort_path=root/'extraction-cohort.json'
    if cohort_path.exists():
        rows=json.loads(cohort_path.read_text())['rows']
    else:
        rows=metadata(args, route, benchmark, fraction)
        study.write_json(cohort_path,{'rows':rows,'max_id':args.max_id,'train_fraction':fraction,
            'contract':'Frozen requested identities and labels; each completed batch stores paired feature matrices and report fingerprints.'})
    paths = {name: root / name / 'feature_spec.json' for name in ('current', 'previous', 'expanded')}
    paths = {name: path for name, path in paths.items() if path.exists()}
    envs = {name: json.loads((root/name/'benchmark.json').read_text())['feature_env'] for name in paths}
    chunks = {name: [] for name in paths}
    kept = []
    digest = hashlib.sha256()
    LOG.info('%s: extracting %d layouts for %d frozen identities, train fraction %.4f', route, len(paths), len(rows), fraction)
    with futures.ProcessPoolExecutor(max_workers=args.workers,
            mp_context=multiprocessing.get_context('spawn'),
            initializer=init_worker, initargs=(args.db, paths, envs)) as pool:
        batches = ((str(root/'extraction-chunks'),i//256,rows[i:i+256]) for i in range(0,len(rows),256))
        for index, (actual, matrices, fingerprints) in enumerate(pool.map(checkpointed_batch, batches, buffersize=2 * args.workers)):
            kept.extend(actual)
            digest.update(fingerprints)
            for name, matrix in matrices.items():
                chunks[name].append(matrix)
            if index % 100 == 0:
                LOG.info('%s: paired extraction %d/%d rows', route, len(kept), len(rows))
    ids = np.asarray([r[0] for r in kept])
    y = np.asarray([r[1] for r in kept], np.float32)
    dev_mask = np.asarray([r[2] for r in kept], bool)
    meta = {r[0]: (r[3], r[4]) for r in kept}
    for name in paths:
        matrix = sparse.vstack(chunks[name], format='csr')
        chunks[name].clear()
        for part, mask in [('train', ~dev_mask), ('dev', dev_mask)]:
            study.save_matrix(root / name, part, matrix[mask], y[mask], ids[mask], meta)
    for part, mask in [('train', ~dev_mask), ('dev', dev_mask)]:
        np.save(root / f'{part}-scores.npy', np.asarray([r[5] for r in kept])[mask])
    study.write_json(root / 'prepared.json', {'requested_rows': len(rows), 'kept_rows': len(kept),
        'paired_input_sha256': digest.hexdigest(), 'train_fraction': fraction,
        'input_contract': 'Both feature layouts extracted from the same fetched report and metadata per row.',
        'test_rows': 0})


def saved_predictions(root, layout, x, threads):
    directory = root / layout
    native = sorted((directory / 'models').glob('seed_*.txt'))
    if native:
        return {int(p.stem.split('_')[-1]): study.predict(lgb.Booster(model_file=str(p)), x, threads)[2] for p in native}
    onnx = sorted((directory / 'models').glob('*.onnx'))
    os.environ['COLLIMATOR_ONNX_THREADS'] = str(threads)
    members = model.load_onnx_models(onnx)
    return {i: np.asarray(m.predict(x), np.float32) for i, m in enumerate(members)}


def benchmark_for(args, route):
    if route != 'general':
        benchmark=json.loads((args.source / route / 'benchmark.json').read_text())
        if args.base_feature_env:
            base=json.loads(args.base_feature_env.read_text())['feature_env']
            benchmark['feature_env']={**base,**benchmark['feature_env']}
        return benchmark
    run = json.loads(args.general_run.read_text())
    source_spec = args.source / 'general/feature_spec.json'
    if json.loads(source_spec.read_text())['total_features'] != run['n_features']:
        raise ValueError('General training metadata does not match feature count')
    return {'train_rows': run['train_rows'], 'feature_env': run['feature_env'],
            'train_config': run['train_config'],
            'min_malware_training_score': run['experiment_spec']['filters']['min_malware_training_score']}


def assessment_admission(before, after, objective='recall'):
    failures = []
    if not after['target_malware']:
        failures.append('no assessment malware in targeted slices')
    elif objective == 'ap' and after['target_ap'] <= before['target_ap']:
        failures.append('target AP did not improve')
    elif objective != 'ap' and after['target_recall_1fp'] <= before['target_recall_1fp']:
        failures.append('target recall at one FP did not improve')
    if (after['ap'] or 0) < (before['ap'] or 0) - .002:
        failures.append('overall assessment AP declined by more than 0.2pp')
    for ft, old in before['by_filetype'].items():
        new = after['by_filetype'][ft]
        if old['malware'] and new['at_fp']['1']['tp'] < old['at_fp']['1']['tp']:
            failures.append(f'{ft}: assessment recall at one FP declined')
    return failures


def malware_cutoff_masks(labels,scores,fit,stop,cutoff):
    """A malware cutoff filters both fitting and stopping, never benign rows."""
    eligible=(labels==0)|(scores>=cutoff)
    return fit & eligible,stop & eligible


def run_route(args, route, targets):
    logging.basicConfig(level=logging.INFO, format='%(asctime)s %(name)s: %(message)s')
    root = args.output / route
    root.mkdir(parents=True, exist_ok=True)
    os.environ.update(COLLIMATOR_MEM_RESERVE_GB='2', COLLIMATOR_MEM_CEILING_GB='80',
                      COLLIMATOR_FIT_RESOURCE_DIR=str(args.output / 'fit-resources'))
    benchmark = benchmark_for(args, route)
    grid = search_grid(args.grid_json)
    current_only = args.current_layout_only
    if args.reuse:
        prior=args.reuse/route
        old_plan=json.loads((prior/'plan.json').read_text())
        if old_plan['train_cap']!=args.train_cap or old_plan['max_id']!=args.max_id or old_plan['benchmark']!=benchmark:
            raise ValueError('Reuse requires identical source settings and cohort bounds')
        if old_plan.get('current_layout_only', False) != current_only and not args.reuse_matrices_only:
            raise ValueError('Reuse requires identical layout scope')
        if old_plan['grid'] != grid and not args.reuse_matrices_only:
            raise ValueError('Reuse of fitted members requires an identical search grid')
        # Source models, layout and effective extraction environment must still
        # be those used to create the cached feature rows.
        for relative, digest in old_plan['hashes']['current'].items():
            if initial.fingerprint(args.source/route/relative) != digest:
                raise ValueError('Reuse source artifact changed: '+relative)
        names=['current','prepared.json','train-scores.npy','dev-scores.npy']
        if not current_only:
            names.append('previous')
        if getattr(args,'expanded_layout',None):
            expanded_source=args.expanded_layout/route
            for relative,digest in old_plan['hashes']['expanded'].items():
                if initial.fingerprint(expanded_source/relative)!=digest:
                    raise ValueError('Expanded reuse source artifact changed: '+relative)
            if json.loads((expanded_source/'benchmark.json').read_text())!=old_plan['expanded_benchmark']:
                raise ValueError('Expanded reuse environment changed')
            names.append('expanded')
        if not args.reuse_matrices_only:
            names.append('fits')
        for name in names:
            if (prior/name).exists() and not (root/name).exists():
                (root/name).symlink_to((prior/name).resolve(),target_is_directory=(prior/name).is_dir())
    previous_benchmark = None
    if current_only:
        pass
    elif route == 'general':
        old_run = json.loads(args.previous_general_run.read_text())
        previous_benchmark = {'feature_env': old_run['feature_env'], 'train_config':old_run['train_config']}
    else:
        previous_metadata = json.loads(args.previous_metadata.read_text())
        previous_benchmark = json.loads(Path(previous_metadata[route]).read_text())
    if previous_benchmark is not None and args.previous_base_feature_env:
        base=json.loads(args.previous_base_feature_env.read_text())['feature_env']
        previous_benchmark['feature_env']={**base,**previous_benchmark['feature_env']}
    restored_cutoff=None
    if getattr(args,'restore_previous_cutoff',False):
        if previous_benchmark is None or 'min_malware_training_score' not in previous_benchmark:
            raise ValueError('Cutoff restoration requires the historical specialist/group benchmark')
        restored_cutoff=previous_benchmark['min_malware_training_score']
        if restored_cutoff<benchmark['min_malware_training_score']:
            raise ValueError('Restoring a lower cutoff needs an expanded training cohort, not filtered cached matrices')
    hashes = {}
    layouts = [('current', args.source), ('previous', args.previous)]
    expanded_benchmark = None
    if getattr(args, 'expanded_layout', None):
        layouts.append(('expanded', args.expanded_layout))
        expanded_benchmark = json.loads((args.expanded_layout/route/'benchmark.json').read_text())
    for layout, bundle in layouts:
        if layout == 'previous' and current_only:
            continue
        source = bundle / route
        if not source.is_dir():
            continue
        hashes[layout] = {str(p.relative_to(source)): initial.fingerprint(p)
                          for p in [source/'feature_spec.json', *sorted((source/'models').glob('*.onnx'))]}
        if not (root/layout).exists():
            shutil.copytree(source, root/layout,ignore=shutil.ignore_patterns('benchmark.json'))
        layout_benchmark = {'current':benchmark,'previous':previous_benchmark,'expanded':expanded_benchmark}[layout]
        initial.freeze(root/layout/'benchmark.json', layout_benchmark)
    initial.freeze(root/'plan.json', {'route':route, 'targets':targets, 'hashes':hashes,
        'grid':grid, 'seeds':list(study.SEEDS), 'train_cap':args.train_cap,
        'ensemble_arithmetic':'f64 accumulation of member probabilities, f32 output',
        **({'current_layout_only': True} if current_only else {}),
        **({'expanded_benchmark': expanded_benchmark} if expanded_benchmark is not None else {}),
        **({'objective':args.metric} if args.metric!='recall' else {}),
        **({'fit_seed_subsets':True} if args.ensemble_subsets else {}),
        **({'protect_filetypes_at_selection': True} if getattr(args,'protect_filetypes_at_selection',False) else {}),
        **({'minimum_members': args.minimum_members} if getattr(args,'minimum_members',1)>1 else {}),
        **({'restore_previous_cutoff':restored_cutoff} if restored_cutoff is not None else {}),
        'max_id':args.max_id, 'benchmark':benchmark, 'previous_benchmark':previous_benchmark,
        'extraction_contract': 'paired route-specific environment, identical fetched report bytes',
        'layout_ablation':route in LAYOUT_ABLATIONS,
        'selection':'Dev halves; on small dev use a training holdout and exclude pretrained models from selection.',
        'assessment':'Frozen winner only; no constituent filetype may lose recall@1FP.',
        'test_usage':'none; historical test metrics identify routes only'})
    if (root/'complete.json').exists():
        return json.loads((root/'complete.json').read_text())
    prepare(args, root, route, benchmark)
    current_train, current_dev = tune.load(root/'current','train'), tune.load(root/'current','dev')
    mode = tune.choose_mode(current_dev)
    fit, stop, x, y, selection, ft = tune.partition_evaluation(current_train, current_dev, mode)
    if (min(np.bincount(current_train[1][fit].astype(int), minlength=2)) < 2
            or not stop.any() or not selection.any() or not (~selection).any()
            or min(np.bincount(y[selection].astype(int), minlength=2)) < 1):
        result = {'route':route,'status':'insufficient independent class support','installed_model_changed':False}
        study.write_json(root/'complete.json',result)
        return result
    cohorts = {'current': (current_train,current_dev,x)}
    for layout in ('previous','expanded'):
        if not (root/layout).exists():
            continue
        pt,pd = tune.load(root/layout,'train'),tune.load(root/layout,'dev')
        px = tune.partition_evaluation(pt,pd,mode)[2]
        cohorts[layout]=(pt,pd,px)
    predictions, records = {}, []
    for layout, (_,_,matrix) in cohorts.items():
        if layout == 'expanded':
            continue  # Newly discovered vocabulary has no pretrained model.
        saved = saved_predictions(root,layout,matrix,args.threads)
        ensembles = [tuple(saved)]
        if layout == 'current' and mode == 'dev_halves':
            ensembles += [s for n in range(1,len(saved)) for s in itertools.combinations(saved,n)]
        for seeds in ensembles:
            key=f'{layout}:'+','.join(map(str,seeds))
            p=study.ensemble_probability([saved[s] for s in seeds])
            predictions[key]=p
            records.append({'key':key,'layout':layout,'variant':'saved','seeds':list(seeds),
                            'selection':filetype_profile(y[selection],p[selection],ft[selection],targets)})
    current=records[0]
    # The old predictor is a diagnosis baseline, not a restoration selected from
    # training rows. Previous-layout refits below are eligible on held-out rows.
    cases=[('current',name,overrides,fit) for name,overrides in grid.items()]
    if 'expanded' in cohorts:
        cases += [('expanded',name,overrides,fit) for name,overrides in grid.items()]
    if 'previous' in cohorts:
        cases.append(('previous','previous_recipe',previous_benchmark['train_config'],fit))
    if restored_cutoff is not None:
        cases += [('current','control_restored_cutoff',{},fit),
                  ('previous','previous_recipe_restored_cutoff',previous_benchmark['train_config'],fit)]
    if route in LAYOUT_ABLATIONS and 'previous' in cohorts:
        cases += [('previous',name,GRID[name],fit) for name in ('control','cap5_weight025_no_hnm')]
    min_score=int(benchmark.get('feature_env',{}).get('COLLIMATOR_MIN_SAMPLE_SCORE','0'))
    if min_score>0:
        replay_fit=fit & (np.load(root/'train-scores.npy') >= min_score)
        if min(np.bincount(current_train[1][replay_fit].astype(int),minlength=2))>=2:
            cases.append(('current','historical_score_floor',{},replay_fit))
    for layout,name,overrides,fit_mask in cases:
        training,_,matrix=cohorts[layout]
        stop_mask=stop
        case_cutoff=benchmark['min_malware_training_score']
        if name.endswith('_restored_cutoff'):
            case_cutoff=restored_cutoff
            fit_mask,stop_mask=malware_cutoff_masks(training[1],np.load(root/'train-scores.npy'),fit_mask,stop,case_cutoff)
            if min(np.bincount(training[1][fit_mask].astype(int),minlength=2))<2 or not stop_mask.any():
                LOG.warning('%s: skipping %s; insufficient fitting/stopping support',route,name)
                continue
        workspace=root/'fits'/layout
        workspace.mkdir(parents=True,exist_ok=True)
        LOG.info('%s: fitting %s/%s on %d rows',route,layout,name,int(fit_mask.sum()))
        xt=training[0][fit_mask]
        with fit_reservation(estimate_fit_gb(xt,SimpleNamespace(n_folds=0,num_threads=args.threads))):
            study.fit_variant(SimpleNamespace(output=workspace,threads=args.threads),name,overrides,
                xt,training[1][fit_mask],training[0][stop_mask],training[1][stop_mask],matrix,y,selection,
                {**benchmark['train_config'],'learner':'azoth'})
        per_seed={s:np.load(workspace/'results'/f'{name}_seed{s}'/'predictions.npz')['probability'] for s in study.SEEDS}
        for seeds in memberships(study.SEEDS,args.ensemble_subsets):
            key=f'{layout}/{name}' + (':'+','.join(map(str,seeds)) if len(seeds)!=len(study.SEEDS) else '')
            p=study.ensemble_probability([per_seed[s] for s in seeds])
            predictions[key]=p
            records.append({'key':key,'layout':layout,'variant':name,'seeds':list(seeds),
                            **({'min_malware_training_score':case_cutoff} if name.endswith('_restored_cutoff') else {}),
                            'selection':filetype_profile(y[selection],p[selection],ft[selection],targets)})
    # Retrained control is the only fair reference when selection rows were
    # seen during production fitting. Saved predictors never enter that choice.
    eligible=[r for r in records if r['layout']!='previous' or r['variant']!='saved']
    if mode!='dev_halves':
        eligible=[r for r in eligible if r['variant']!='saved']
    eligible=[r for r in eligible if len(r['seeds'])>=getattr(args,'minimum_members',1)]
    reference=next(r for r in records if r['key']=='current/control') if mode!='dev_halves' else current
    winner=choose(eligible,reference,args.metric,getattr(args,'protect_filetypes_at_selection',False))
    initial.freeze(root/'frozen-winner.json',{'mode':mode,'winner':winner,'comparisons':records})
    assessment=~selection
    reports={r['key']:filetype_profile(y[assessment],predictions[r['key']][assessment],ft[assessment],targets)
             for r in [current,winner]+[r for r in records if r['layout']=='previous' and r['variant']=='saved']}
    before,after=reports[current['key']],reports[winner['key']]
    failures=assessment_admission(before,after,args.metric)
    result={'route':route,'targets':targets,'mode':mode,'winner':winner['key'],
            'objective':args.metric,
            'assessment':reports,'target_recall_1fp_delta': None if not after['target_malware'] else after['target_recall_1fp']-before['target_recall_1fp'],
            'status':'held_back' if failures else 'improved_research_candidate',
            'reasons':failures,'installed_model_changed':False,
            'limitation':'Bounded training screen; full-population refit and deployment confirmation still required.'}
    if not failures:
        dest=root/'candidate';(dest/'models').mkdir(parents=True,exist_ok=True)
        shutil.copy2(root/winner['layout']/'feature_spec.json',dest/'feature_spec.json')
        spec=features.FeatureSpec.load(dest/'feature_spec.json')
        for seed in winner['seeds']:
            txt=(root/'current/models'/f'seed_{seed}.txt' if winner['variant']=='saved' else
                 root/'fits'/winner['layout']/'results'/f"{winner['variant']}_seed{seed}"/'model.txt')
            shutil.copy2(txt,dest/'models'/f'seed_{seed}.txt')
            if not export.export_lightgbm_onnx(lgb.Booster(model_file=str(txt)),spec.total_features,dest/'models'/f'seed_{seed}.onnx'):
                raise ValueError('ONNX export failed')
        actual=study.ensemble_probability([m.predict(cohorts[winner['layout']][2][assessment]) for m in model.load_onnx_models(sorted((dest/'models').glob('*.onnx')))])
        error=float(np.max(np.abs(actual-predictions[winner['key']][assessment])))
        result['onnx_max_difference']=error
        if error>1e-4:
            result['status']='held_back';result['reasons'].append('ONNX probability parity failed')
        study.write_json(dest/'research.json',result)
    study.write_json(root/'complete.json',result)
    LOG.info('%s: %s delta=%s winner=%s',route,result['status'],result['target_recall_1fp_delta'],winner['key'])
    return result


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--source',type=Path,default=Path('out/models/azoth'))
    p.add_argument('--previous',type=Path,default=Path('/home/t/src/azoth'))
    p.add_argument('--comparison',type=Path,default=Path('out/deployments/20261031-recovery/detection-comparison.json'))
    p.add_argument('--general-run',type=Path,default=Path('out/experiments/azoth/runs/2026-10-31T07-43-33-experiment.json'))
    p.add_argument('--previous-general-run',type=Path,default=Path('out/experiments/azoth/runs/2026-10-26T17-19-22-experiment.json'))
    p.add_argument('--base-feature-env',type=Path,help='Inherited nightly environment beneath specialist overrides')
    p.add_argument('--previous-base-feature-env',type=Path,help='Explicit inherited baseline for historical override-only metadata')
    p.add_argument('--previous-metadata',type=Path,default=Path('out/experiments/regression-diagnosis-20261031/verified-previous-metadata.json'))
    p.add_argument('--output',type=Path,default=Path('out/experiments/regression-recovery-20261031'))
    p.add_argument('--routes',nargs='+')
    p.add_argument('--metric',choices=['recall','ap'],default='recall')
    p.add_argument('--ensemble-subsets',action='store_true')
    p.add_argument('--protect-filetypes-at-selection',action='store_true',help='Reject selection gains that cost another filetype recall before choosing a winner')
    p.add_argument('--minimum-members',type=int,default=1,choices=(1,2,3),help='Minimum ensemble size eligible for selection')
    p.add_argument('--restore-previous-cutoff',action='store_true',help='Also fit current/historical recipes with the historical malware-score eligibility filter restored')
    p.add_argument('--grid-json',type=Path,help='Frozen named training overrides, including an unchanged control')
    p.add_argument('--current-layout-only',action='store_true',help='Optimize the current vocabulary without extracting the historical layout')
    p.add_argument('--expanded-layout',type=Path,help='Additional train-only vocabulary bundle to fit on the same paired reports')
    p.add_argument('--reuse',type=Path,help='Reuse frozen paired matrices and fitted members from a completed study')
    p.add_argument('--reuse-matrices-only',action='store_true',help='With --reuse, allow a new grid but fit all its members in the new workspace')
    p.add_argument('--db',default='postgres://hopper@localhost:5432/hopper')
    p.add_argument('--max-id',type=int,default=6309383805)
    p.add_argument('--train-cap',type=int,default=300000)
    p.add_argument('--workers',type=int,default=4)
    p.add_argument('--threads',type=int,default=8)
    p.add_argument('--parallelism',type=int,default=2)
    a=p.parse_args();a.output=a.output.resolve();a.output.mkdir(parents=True,exist_ok=True)
    if a.reuse_matrices_only and not a.reuse:
        p.error('--reuse-matrices-only requires --reuse')
    routes=inventory(json.loads(a.comparison.read_text()),a.source,include_ap=a.metric=='ap')
    if a.routes:
        if set(a.routes)-routes.keys():p.error('Requested routes not in regression inventory')
        routes={r:routes[r] for r in a.routes}
    initial.freeze(a.output/'inventory.json',routes)
    results=[]
    with futures.ProcessPoolExecutor(max_workers=a.parallelism,mp_context=multiprocessing.get_context('spawn')) as pool:
        pending={pool.submit(run_route,a,r,t):r for r,t in sorted(routes.items(),key=lambda item:(item[0]=='general',item[0].startswith('filegroups'),item[0]))}
        for future in futures.as_completed(pending):
            route=pending[future]
            try:result=future.result()
            except Exception as exc:
                LOG.exception('FAILED %s',route);result={'route':route,'status':'error','error':str(exc)}
            results.append(result);study.write_json(a.output/'status.json',results)
    return int(any(r['status']=='error' for r in results))


if __name__=='__main__':
    raise SystemExit(main())
