# Promote REJECTED — `2daec8ba255976ab` on `filetypes/csharp`

Generated 2026-08-21T13:36:37Z

confirm did not hold: experiment failed: make experiment exit 2: exit status 2
--- experiment log tail ---
--n-estimators 400 --max-depth 12 \
	--learning-rate 0.05 --early-stopping-rounds 25 \
	--num-leaves 96 \
	--min-child-samples 100 \
	--min-child-weight 5 \
	--colsample-bytree 0.8 --subsample 0.8 \
	--gamma 0 --reg-alpha 0 --reg-lambda 1 \
	--device auto \
	 \
	 \
	--min-malware-score 0 \
	--beta 1.25 --threshold-mode fbeta \
	 \
	--hard-negative-fraction 0.2 --hard-negative-weight 5 \
	--scale-pos-weight-mult 1 \
	--boosting-type gbdt \
	 \
	--seed-search-k 3 \
	--save-all-seeds \
	 \
	 \
	--cache-dir out/cache/experiment/azoth \
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_inherit_from_filetypes_plist_8b54303f_confirm_seedsearch_3.log"
09:35:51 INFO  collimator.experiment: using cached experiment snapshot: max_id=3070481458
09:35:51 INFO  collimator.experiment: dataset snapshot: max_id=3070481458
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/home/t/collimator/src/collimator/__main__.py", line 983, in <module>
    main()
  File "/home/t/collimator/src/collimator/__main__.py", line 901, in main
    experiment.run_experiment(
  File "/home/t/collimator/src/collimator/experiment.py", line 957, in run_experiment
    corpus = sample_partitioned_reports(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/src/collimator/experiment.py", line 478, in sample_partitioned_reports
    for row_id, label, partition, group_id, score in data.stream_partitioned_metadata_grouped(
                                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/src/collimator/data.py", line 911, in stream_partitioned_metadata_grouped
    for row_id, sha256, label, canonical, score in _execute(conn, query, params):
                                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/src/collimator/data.py", line 389, in _execute
    cur.execute(query, params)
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/psycopg/cursor.py", line 117, in execute
    raise ex.with_traceback(None)
psycopg.OperationalError: consuming input failed: server closed the connection unexpectedly
	This probably means the server terminated abnormally
	before or while processing the request.
make[1]: *** [Makefile:1960: experiment] Error 1
make[1]: Leaving directory '/home/t/collimator'
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-08-21T13-35-45_20260821T133545-confirm-2daec8ba255976ab_inherit_from_filetypes_plist_8b54303f_confirm_seedsearch_3.log

## Gates

- **Confirm** (different seed, original profile): **FAIL** — experiment failed: make experiment exit 2: exit status 2
--- experiment log tail ---
--n-estimators 400 --max-depth 12 \
	--learning-rate 0.05 --early-stopping-rounds 25 \
	--num-leaves 96 \
	--min-child-samples 100 \
	--min-child-weight 5 \
	--colsample-bytree 0.8 --subsample 0.8 \
	--gamma 0 --reg-alpha 0 --reg-lambda 1 \
	--device auto \
	 \
	 \
	--min-malware-score 0 \
	--beta 1.25 --threshold-mode fbeta \
	 \
	--hard-negative-fraction 0.2 --hard-negative-weight 5 \
	--scale-pos-weight-mult 1 \
	--boosting-type gbdt \
	 \
	--seed-search-k 3 \
	--save-all-seeds \
	 \
	 \
	--cache-dir out/cache/experiment/azoth \
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_inherit_from_filetypes_plist_8b54303f_confirm_seedsearch_3.log"
09:35:51 INFO  collimator.experiment: using cached experiment snapshot: max_id=3070481458
09:35:51 INFO  collimator.experiment: dataset snapshot: max_id=3070481458
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/home/t/collimator/src/collimator/__main__.py", line 983, in <module>
    main()
  File "/home/t/collimator/src/collimator/__main__.py", line 901, in main
    experiment.run_experiment(
  File "/home/t/collimator/src/collimator/experiment.py", line 957, in run_experiment
    corpus = sample_partitioned_reports(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/src/collimator/experiment.py", line 478, in sample_partitioned_reports
    for row_id, label, partition, group_id, score in data.stream_partitioned_metadata_grouped(
                                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/src/collimator/data.py", line 911, in stream_partitioned_metadata_grouped
    for row_id, sha256, label, canonical, score in _execute(conn, query, params):
                                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/src/collimator/data.py", line 389, in _execute
    cur.execute(query, params)
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/psycopg/cursor.py", line 117, in execute
    raise ex.with_traceback(None)
psycopg.OperationalError: consuming input failed: server closed the connection unexpectedly
	This probably means the server terminated abnormally
	before or while processing the request.
make[1]: *** [Makefile:1960: experiment] Error 1
make[1]: Leaving directory '/home/t/collimator'
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-08-21T13-35-45_20260821T133545-confirm-2daec8ba255976ab_inherit_from_filetypes_plist_8b54303f_confirm_seedsearch_3.log
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `2daec8ba255976ab` | `` | `—` |
| PR AUC | 0.6744 | — | — |
| ROC AUC | 0.9326 | — | — |
| F1 | 0.5595 | — | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: experiment failed: make experiment exit 2: exit status 2
--- experiment log tail ---
--n-estimators 400 --max-depth 12 \
	--learning-rate 0.05 --early-stopping-rounds 25 \
	--num-leaves 96 \
	--min-child-samples 100 \
	--min-child-weight 5 \
	--colsample-bytree 0.8 --subsample 0.8 \
	--gamma 0 --reg-alpha 0 --reg-lambda 1 \
	--device auto \
	 \
	 \
	--min-malware-score 0 \
	--beta 1.25 --threshold-mode fbeta \
	 \
	--hard-negative-fraction 0.2 --hard-negative-weight 5 \
	--scale-pos-weight-mult 1 \
	--boosting-type gbdt \
	 \
	--seed-search-k 3 \
	--save-all-seeds \
	 \
	 \
	--cache-dir out/cache/experiment/azoth \
	2>&1 | tee "out/experiments/azoth/logs/$(date +%Y-%m-%dT%H-%M-%S)-experiment_inherit_from_filetypes_plist_8b54303f_confirm_seedsearch_3.log"
09:35:51 INFO  collimator.experiment: using cached experiment snapshot: max_id=3070481458
09:35:51 INFO  collimator.experiment: dataset snapshot: max_id=3070481458
Traceback (most recent call last):
  File "<frozen runpy>", line 198, in _run_module_as_main
  File "<frozen runpy>", line 88, in _run_code
  File "/home/t/collimator/src/collimator/__main__.py", line 983, in <module>
    main()
  File "/home/t/collimator/src/collimator/__main__.py", line 901, in main
    experiment.run_experiment(
  File "/home/t/collimator/src/collimator/experiment.py", line 957, in run_experiment
    corpus = sample_partitioned_reports(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/src/collimator/experiment.py", line 478, in sample_partitioned_reports
    for row_id, label, partition, group_id, score in data.stream_partitioned_metadata_grouped(
                                                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/src/collimator/data.py", line 911, in stream_partitioned_metadata_grouped
    for row_id, sha256, label, canonical, score in _execute(conn, query, params):
                                                   ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/t/collimator/src/collimator/data.py", line 389, in _execute
    cur.execute(query, params)
  File "/home/t/collimator/.venv/lib/python3.12/site-packages/psycopg/cursor.py", line 117, in execute
    raise ex.with_traceback(None)
psycopg.OperationalError: consuming input failed: server closed the connection unexpectedly
	This probably means the server terminated abnormally
	before or while processing the request.
make[1]: *** [Makefile:1960: experiment] Error 1
make[1]: Leaving directory '/home/t/collimator'
--- end log tail ---
full log: /home/t/collimator/out/autocollie/runs/2026-08-21T13-35-45_20260821T133545-confirm-2daec8ba255976ab_inherit_from_filetypes_plist_8b54303f_confirm_seedsearch_3.log
