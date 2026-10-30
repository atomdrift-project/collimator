# Promote REJECTED — `d9c6863d435e4f50` on `filetypes/registry`

Generated 2026-10-30T17:42:53Z

azoth-validate failed: exit status 2 (log /home/t/src/collimator/out/autocollie/runs/2026-10-30T13-40-57_20261030T134018-promote-d9c6863d435e4f50_azoth-validate.log; tail:   File "/usr/lib/python3.14/concurrent/futures/process.py", line 234, in _process_worker
    initializer(*initargs)
    ~~~~~~~~~~~^^^^^^^^^^^
  File "/home/t/src/collimator/src/collimator/features.py", line 4971, in _init_extract_worker
    _worker_ctx = _ExtractContext(spec)
  File "/home/t/src/collimator/src/collimator/features.py", line 2564, in __init__
    for source, words in spec.keyword_vocabs.items()
                         ^^^^^^^^^^^^^^^^^^^
AttributeError: 'FeatureSpec' object has no attribute 'keyword_vocabs'
Traceback (most recent call last):
  File "/home/t/src/collimator/scripts/azoth_calibrate_ensemble.py", line 1682, in <module>
    raise SystemExit(main())
                     ~~~~^^
  File "/home/t/src/collimator/scripts/azoth_calibrate_ensemble.py", line 1566, in main
    route_scores.extend(_run_score_jobs(score_jobs, row_ids, args.parallelism, args.log_level))
                        ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/src/collimator/scripts/azoth_calibrate_ensemble.py", line 1328, in _run_score_jobs
    results.append(_score_route_worker(dict(job, row_index=index)))
                   ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/src/collimator/src/collimator/profiling.py", line 64, in wrapped
    return fn(*args, **kwargs)
  File "/home/t/src/collimator/scripts/azoth_calibrate_ensemble.py", line 1278, in _score_route_worker
    return _score_route(
        job["db_path"],
    ...<8 lines>...
        cache_context=job.get("cache_context"),
    )
  File "/home/t/src/collimator/scripts/azoth_calibrate_ensemble.py", line 400, in _score_route
    return _score_route_impl(db_path, route, **options)
  File "/home/t/src/collimator/scripts/azoth_calibrate_ensemble.py", line 501, in _score_route_impl
    for block, block_labels in features.extract_labeled_from_db_batches(
                               ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        db_path, rows, spec, n_workers=workers,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ):
    ^
  File "/home/t/src/collimator/src/collimator/features.py", line 5768, in extract_labeled_from_db_batches
        spec = _worker_spec
            ^^^^^^^^^^^^^^^
    ...<3 lines>...
    blocks, labels = [], []
    ^^^^^^^^^
  File "/home/t/src/collimator/src/collimator/features.py", line 5363, in _bounded_ordered_dynamic_iter
    """
    
  File "/usr/lib/python3.14/concurrent/futures/process.py", line 898, in submit
    raise BrokenProcessPool(self._broken)
concurrent.futures.process.BrokenProcessPool: A child process terminated abruptly, the process pool is not usable anymore
make[1]: *** [Makefile:1248: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/src/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — averaged 3-seed ensemble PR_AUC held: 0.9574 -> 0.9606; individual seeds may be noisy
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d9c6863d435e4f50` | `e5167b74bf767a47` | `e9ca3fad07e7958b` |
| PR AUC | 0.9574 | 0.9606 | 0.9607 |
| ROC AUC | 0.9996 | 0.9997 | 0.9997 |
| F1 | 0.8413 | 0.8595 | 0.8739 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/src/collimator/out/autocollie/runs/2026-10-30T13-40-57_20261030T134018-promote-d9c6863d435e4f50_azoth-validate.log; tail:   File "/usr/lib/python3.14/concurrent/futures/process.py", line 234, in _process_worker
    initializer(*initargs)
    ~~~~~~~~~~~^^^^^^^^^^^
  File "/home/t/src/collimator/src/collimator/features.py", line 4971, in _init_extract_worker
    _worker_ctx = _ExtractContext(spec)
  File "/home/t/src/collimator/src/collimator/features.py", line 2564, in __init__
    for source, words in spec.keyword_vocabs.items()
                         ^^^^^^^^^^^^^^^^^^^
AttributeError: 'FeatureSpec' object has no attribute 'keyword_vocabs'
Traceback (most recent call last):
  File "/home/t/src/collimator/scripts/azoth_calibrate_ensemble.py", line 1682, in <module>
    raise SystemExit(main())
                     ~~~~^^
  File "/home/t/src/collimator/scripts/azoth_calibrate_ensemble.py", line 1566, in main
    route_scores.extend(_run_score_jobs(score_jobs, row_ids, args.parallelism, args.log_level))
                        ~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/src/collimator/scripts/azoth_calibrate_ensemble.py", line 1328, in _run_score_jobs
    results.append(_score_route_worker(dict(job, row_index=index)))
                   ~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/src/collimator/src/collimator/profiling.py", line 64, in wrapped
    return fn(*args, **kwargs)
  File "/home/t/src/collimator/scripts/azoth_calibrate_ensemble.py", line 1278, in _score_route_worker
    return _score_route(
        job["db_path"],
    ...<8 lines>...
        cache_context=job.get("cache_context"),
    )
  File "/home/t/src/collimator/scripts/azoth_calibrate_ensemble.py", line 400, in _score_route
    return _score_route_impl(db_path, route, **options)
  File "/home/t/src/collimator/scripts/azoth_calibrate_ensemble.py", line 501, in _score_route_impl
    for block, block_labels in features.extract_labeled_from_db_batches(
                               ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        db_path, rows, spec, n_workers=workers,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    ):
    ^
  File "/home/t/src/collimator/src/collimator/features.py", line 5768, in extract_labeled_from_db_batches
        spec = _worker_spec
            ^^^^^^^^^^^^^^^
    ...<3 lines>...
    blocks, labels = [], []
    ^^^^^^^^^
  File "/home/t/src/collimator/src/collimator/features.py", line 5363, in _bounded_ordered_dynamic_iter
    """
    
  File "/usr/lib/python3.14/concurrent/futures/process.py", line 898, in submit
    raise BrokenProcessPool(self._broken)
concurrent.futures.process.BrokenProcessPool: A child process terminated abruptly, the process pool is not usable anymore
make[1]: *** [Makefile:1248: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/src/collimator')
