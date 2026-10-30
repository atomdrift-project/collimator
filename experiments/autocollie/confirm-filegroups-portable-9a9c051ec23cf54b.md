# Confirm FAIL — 9a9c051ec23cf54b on `filegroups/portable`

Cycle `20261029T023455-confirm-9a9c051ec23cf54b` — 2026-10-29T02:34:55Z

experiment failed: make experiment exit 2: exit status 2
--- experiment log tail ---
File "<frozen runpy>", line 203, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/home/t/src/collimator/src/collimator/__main__.py", line 989, in <module>
    main()
    ~~~~^^
  File "/home/t/src/collimator/src/collimator/__main__.py", line 906, in main
    experiment.run_experiment(
    ~~~~~~~~~~~~~~~~~~~~~~~~~^
        db_path=_db_dsn(args.db),
        ^^^^^^^^^^^^^^^^^^^^^^^^^
    ...<44 lines>...
        rerun_existing=args.rerun_existing,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    )
    ^
  File "/home/t/src/collimator/src/collimator/experiment.py", line 1127, in run_experiment
    spec = features.build_vocab_from_db(
        db_path,
    ...<2 lines>...
        **vocab_options,
    )
  File "/home/t/src/collimator/src/collimator/profiling.py", line 64, in wrapped
    return fn(*args, **kwargs)
  File "/home/t/src/collimator/src/collimator/features.py", line 6146, in build_vocab_from_db
    spec = _build_vocab_from_db(db_path, row_ids_labels, n_workers, counts, scratch,
                               shared_cache_dir=shared_cache_dir, row_folds=row_folds)
  File "/home/t/src/collimator/src/collimator/features.py", line 6514, in _build_vocab_from_db
    summary = _count_vocab_rows(db_path, row_ids_labels, n_workers, counts, scratch)
  File "/home/t/src/collimator/src/collimator/features.py", line 6254, in _count_vocab_rows
    for res, sealed, n_rows in _memory_budgeted_unordered_iter(
                               ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~^
        pool, _vocab_labeled_db_shard_worker, batch_args,
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
        n_workers=nw,
        ^^^^^^^^^^^^^
    ):
    ^
  File "/home/t/src/collimator/src/collimator/features.py", line 5387, in _memory_budgeted_unordered_iter
    yield from _bounded_unordered_iter(pool, fn, it, max_inflight=budget)
  File "/home/t/src/collimator/src/collimator/features.py", line 5368, in _bounded_unordered_iter
    yield future.result()
          ~~~~~~~~~~~~~^^
  File "/usr/lib/python3.14/concurrent/futures/_base.py", line 447, in result
    return self.__get_result()
           ~~~~~~~~~~~~~~~~~^^
  File "/usr/lib/python3.14/concurrent/futures/_base.py", line 396, in __get_result
    raise self._exception
psycopg.errors.AdminShutdown: terminating connection due to administrator command
make[1]: Leaving directory '/home/t/src/collimator'
make[1]: *** [Makefile:2100: experiment] Error 1
--- end log tail ---
full log: /home/t/src/collimator/out/autocollie/runs/2026-10-29T02-34-55_20261029T023455-confirm-9a9c051ec23cf54b_portable_training_leaves128_reg2_confirm_seedsearch_3.log

## Per-seed results (1 ran)

| | original | seed=43 | 
|---|---|---|
| key | `9a9c051ec23cf54b` | `` |
| PR AUC | 0.9438 | 0.0000 |
| ROC AUC | 0.9856 | 0.0000 |
| Recall@L50 | — | — |
| verdict | — | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/1 held). Suggest abandoning the idea or letting the LLM propose a variant.
