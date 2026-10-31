# Promote REJECTED — `4a33080fdc16e443` on `filegroups/documents`

Generated 2026-10-30T21:18:30Z

confirm did not hold: experiment failed: make experiment exit 2: exit status 2
--- experiment log tail ---
17:18:21 INFO  collimator.vocabulary: vocab expansion: 2/2 partitions checkpointed, 33.7s elapsed
17:18:22 INFO  collimator.features: trigram shortlist: round 1, 4096 candidates, 0/500 accepted so far
17:18:22 INFO  collimator.features: trigram prevalence benign-shortlist-0: 108078 benign rows, 0/317 batches resumed
17:18:22 INFO  collimator.features: mem-aware workers: 12 workers fit (headroom=81 GB after reserve=48 GB, per_worker=2.0 GB)
17:18:22 INFO  collimator.features: vocab worker budget: initial -> 12/12 workers; rechecking every 30s
17:18:24 INFO  collimator.features: trigram prevalence benign-shortlist-0: 317/317 batches processed, 1.9s elapsed
17:18:24 INFO  collimator.features: trigram selection complete: 4096 shortlist candidates tested, 500 selected, 1 rounds, exhaustive fallback=False
17:18:25 INFO  collimator.features: extended metrics: 29 keys from 5000 scanned rows (always-keep below threshold: ast_depth_capped)
17:18:26 INFO  collimator.features: crit-category n-grams: 26 unigrams, 134 bigrams, 432 trigrams from 5000 scanned rows
17:18:27 INFO  collimator.features: ATT&CK/MBC n-grams: 500/500 atk bi/tri, 466/500 mbc bi/tri from 5000 scanned rows
17:18:27 INFO  collimator.features: feature vocabulary: 16945 columns (no fixed name filter)
17:18:27 INFO  collimator.features: vocab: 523 paths, 53 filetypes, 1555 elements, 2415 bigrams, 11 ghosts, 29 ext_metrics -> 16945 features
Traceback (most recent call last):
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
  File "/home/t/src/collimator/src/collimator/corpus_snapshot.py", line 42, in wrapped
    return fn(db_path, *args, **kwargs)
  File "/home/t/src/collimator/src/collimator/experiment.py", line 1141, in run_experiment
    spec = features.build_vocab_from_db(
        db_path,
    ...<2 lines>...
        **vocab_options,
    )
  File "/home/t/src/collimator/src/collimator/profiling.py", line 64, in wrapped
    return fn(*args, **kwargs)
  File "/home/t/src/collimator/src/collimator/features.py", line 6362, in build_vocab_from_db
    for _ in _count_keyword_reports(reports(), keywords):
             ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/src/collimator/src/collimator/features.py", line 2408, in _count_keyword_reports
    for source, words in _report_keywords(report_files(report), counters).items():
                         ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/src/collimator/src/collimator/features.py", line 2386, in _report_keywords
    raise ValueError(
    ...<2 lines>...
    )
ValueError: description keywords require descriptions: 1 rule IDs missing descriptions in report; examples: third_party/elastic/Multi_EICAR/multi/eicar
make: *** [Makefile:2122: experiment] Error 1
--- end log tail ---
full log: /home/t/src/collimator/out/autocollie/runs/2026-10-30T21-06-02_20261030T210602-confirm-4a33080fdc16e443_try_rule_keywords_false_description_keywords_true_keyword_vocab_max_10000_keyword_min_freq_1_confirm_seedsearch_3.log

## Gates

- **Confirm** (different seed, original profile): **FAIL** — experiment failed: make experiment exit 2: exit status 2
--- experiment log tail ---
17:18:21 INFO  collimator.vocabulary: vocab expansion: 2/2 partitions checkpointed, 33.7s elapsed
17:18:22 INFO  collimator.features: trigram shortlist: round 1, 4096 candidates, 0/500 accepted so far
17:18:22 INFO  collimator.features: trigram prevalence benign-shortlist-0: 108078 benign rows, 0/317 batches resumed
17:18:22 INFO  collimator.features: mem-aware workers: 12 workers fit (headroom=81 GB after reserve=48 GB, per_worker=2.0 GB)
17:18:22 INFO  collimator.features: vocab worker budget: initial -> 12/12 workers; rechecking every 30s
17:18:24 INFO  collimator.features: trigram prevalence benign-shortlist-0: 317/317 batches processed, 1.9s elapsed
17:18:24 INFO  collimator.features: trigram selection complete: 4096 shortlist candidates tested, 500 selected, 1 rounds, exhaustive fallback=False
17:18:25 INFO  collimator.features: extended metrics: 29 keys from 5000 scanned rows (always-keep below threshold: ast_depth_capped)
17:18:26 INFO  collimator.features: crit-category n-grams: 26 unigrams, 134 bigrams, 432 trigrams from 5000 scanned rows
17:18:27 INFO  collimator.features: ATT&CK/MBC n-grams: 500/500 atk bi/tri, 466/500 mbc bi/tri from 5000 scanned rows
17:18:27 INFO  collimator.features: feature vocabulary: 16945 columns (no fixed name filter)
17:18:27 INFO  collimator.features: vocab: 523 paths, 53 filetypes, 1555 elements, 2415 bigrams, 11 ghosts, 29 ext_metrics -> 16945 features
Traceback (most recent call last):
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
  File "/home/t/src/collimator/src/collimator/corpus_snapshot.py", line 42, in wrapped
    return fn(db_path, *args, **kwargs)
  File "/home/t/src/collimator/src/collimator/experiment.py", line 1141, in run_experiment
    spec = features.build_vocab_from_db(
        db_path,
    ...<2 lines>...
        **vocab_options,
    )
  File "/home/t/src/collimator/src/collimator/profiling.py", line 64, in wrapped
    return fn(*args, **kwargs)
  File "/home/t/src/collimator/src/collimator/features.py", line 6362, in build_vocab_from_db
    for _ in _count_keyword_reports(reports(), keywords):
             ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/src/collimator/src/collimator/features.py", line 2408, in _count_keyword_reports
    for source, words in _report_keywords(report_files(report), counters).items():
                         ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/src/collimator/src/collimator/features.py", line 2386, in _report_keywords
    raise ValueError(
    ...<2 lines>...
    )
ValueError: description keywords require descriptions: 1 rule IDs missing descriptions in report; examples: third_party/elastic/Multi_EICAR/multi/eicar
make: *** [Makefile:2122: experiment] Error 1
--- end log tail ---
full log: /home/t/src/collimator/out/autocollie/runs/2026-10-30T21-06-02_20261030T210602-confirm-4a33080fdc16e443_try_rule_keywords_false_description_keywords_true_keyword_vocab_max_10000_keyword_min_freq_1_confirm_seedsearch_3.log
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `4a33080fdc16e443` | `` | `—` |
| PR AUC | 0.9979 | — | — |
| ROC AUC | 0.9977 | — | — |
| F1 | 0.9717 | — | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: experiment failed: make experiment exit 2: exit status 2
--- experiment log tail ---
17:18:21 INFO  collimator.vocabulary: vocab expansion: 2/2 partitions checkpointed, 33.7s elapsed
17:18:22 INFO  collimator.features: trigram shortlist: round 1, 4096 candidates, 0/500 accepted so far
17:18:22 INFO  collimator.features: trigram prevalence benign-shortlist-0: 108078 benign rows, 0/317 batches resumed
17:18:22 INFO  collimator.features: mem-aware workers: 12 workers fit (headroom=81 GB after reserve=48 GB, per_worker=2.0 GB)
17:18:22 INFO  collimator.features: vocab worker budget: initial -> 12/12 workers; rechecking every 30s
17:18:24 INFO  collimator.features: trigram prevalence benign-shortlist-0: 317/317 batches processed, 1.9s elapsed
17:18:24 INFO  collimator.features: trigram selection complete: 4096 shortlist candidates tested, 500 selected, 1 rounds, exhaustive fallback=False
17:18:25 INFO  collimator.features: extended metrics: 29 keys from 5000 scanned rows (always-keep below threshold: ast_depth_capped)
17:18:26 INFO  collimator.features: crit-category n-grams: 26 unigrams, 134 bigrams, 432 trigrams from 5000 scanned rows
17:18:27 INFO  collimator.features: ATT&CK/MBC n-grams: 500/500 atk bi/tri, 466/500 mbc bi/tri from 5000 scanned rows
17:18:27 INFO  collimator.features: feature vocabulary: 16945 columns (no fixed name filter)
17:18:27 INFO  collimator.features: vocab: 523 paths, 53 filetypes, 1555 elements, 2415 bigrams, 11 ghosts, 29 ext_metrics -> 16945 features
Traceback (most recent call last):
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
  File "/home/t/src/collimator/src/collimator/corpus_snapshot.py", line 42, in wrapped
    return fn(db_path, *args, **kwargs)
  File "/home/t/src/collimator/src/collimator/experiment.py", line 1141, in run_experiment
    spec = features.build_vocab_from_db(
        db_path,
    ...<2 lines>...
        **vocab_options,
    )
  File "/home/t/src/collimator/src/collimator/profiling.py", line 64, in wrapped
    return fn(*args, **kwargs)
  File "/home/t/src/collimator/src/collimator/features.py", line 6362, in build_vocab_from_db
    for _ in _count_keyword_reports(reports(), keywords):
             ~~~~~~~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/src/collimator/src/collimator/features.py", line 2408, in _count_keyword_reports
    for source, words in _report_keywords(report_files(report), counters).items():
                         ~~~~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/src/collimator/src/collimator/features.py", line 2386, in _report_keywords
    raise ValueError(
    ...<2 lines>...
    )
ValueError: description keywords require descriptions: 1 rule IDs missing descriptions in report; examples: third_party/elastic/Multi_EICAR/multi/eicar
make: *** [Makefile:2122: experiment] Error 1
--- end log tail ---
full log: /home/t/src/collimator/out/autocollie/runs/2026-10-30T21-06-02_20261030T210602-confirm-4a33080fdc16e443_try_rule_keywords_false_description_keywords_true_keyword_vocab_max_10000_keyword_min_freq_1_confirm_seedsearch_3.log
