# Promote REJECTED — `87866efc2330c865` on `filetypes/package.json`

Generated 2026-11-07T02:00:39Z

azoth-validate failed: signal: terminated (log /home/t/src/collimator/out/autocollie/runs/2026-11-06T19-56-14_20261106T195515-promote-87866efc2330c865_azoth-validate.log; tail: 2026-11-06 20:54:09,926 INFO collimator.model: ONNX input projection: 10252 -> 2023 columns across 3 members
2026-11-06 20:54:10,091 INFO collimator.features: DB-backed feature extraction: 13772 rows, 16 workers, batch_size=1024
2026-11-06 20:54:10,092 INFO collimator.features: mem-aware workers: 16 workers fit (headroom=42 GB after reserve=2 GB, per_worker=2.0 GB)
2026-11-06 20:54:10,092 INFO collimator.features: extraction worker budget: initial -> 16/16; preserving row order
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
2026-11-06 20:54:17,067 INFO collimator.matrix_store: disk-backed matrix ready: 13772 rows, 10440129 nnz, 0.12 GiB; scratch=/home/t/src/collimator/out/cache/matrix-scratch/matrix-zsvuy85h
2026-11-06 20:54:17,158 INFO azoth_calibrate_ensemble: filegroups/crx_selected: saved route feature matrix cache out/cache/azoth-route-features/filegroups_crx_selected-6641136469-7a599eb89e8c713a-1284d3d2472c4226.matrix.npz
2026-11-06 20:54:17,475 INFO azoth_calibrate_ensemble: filegroups/crx_selected: refreshed 13772 rows in 7.7s (fetch 0.1s, filter 0.0s, load 0.0s, extract 7.1s, matrix 0.0s, predict 0.1s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.1s; features=10252 nnz=10440129)
2026-11-06 20:54:17,485 INFO azoth_calibrate_ensemble: scoring filegroups/data_recovery
2026-11-06 20:54:17,496 INFO azoth_calibrate_ensemble: filegroups/data_recovery: score identity changed; refreshing
2026-11-06 20:54:27,446 INFO collimator.model: ONNX input projection: 128071 -> 464 columns across 3 members
2026-11-06 20:54:28,976 INFO collimator.features: DB-backed feature extraction: 167978 rows, 16 workers, batch_size=1024
2026-11-06 20:54:28,977 INFO collimator.features: mem-aware workers: 16 workers fit (headroom=42 GB after reserve=2 GB, per_worker=2.0 GB)
2026-11-06 20:54:28,977 INFO collimator.features: extraction worker budget: initial -> 16/16; preserving row order
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
2026-11-06 20:54:43,878 INFO collimator.matrix_store: disk-backed matrix ready: 167978 rows, 6749983 nnz, 0.08 GiB; scratch=/home/t/src/collimator/out/cache/matrix-scratch/matrix-x2t3b0wy
2026-11-06 20:54:46,079 INFO azoth_calibrate_ensemble: filegroups/data_recovery: refreshed 167978 rows in 28.6s (fetch 9.9s, filter 0.0s, load 0.1s, extract 16.4s, matrix 0.0s, predict 1.0s, write 0.2s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=128071 nnz=6749983)
2026-11-06 20:54:46,092 INFO azoth_calibrate_ensemble: scoring filegroups/filegroups_archive_oct26
2026-11-06 20:54:46,104 INFO azoth_calibrate_ensemble: filegroups/filegroups_archive_oct26: score identity changed; refreshing
2026-11-06 20:54:50,250 INFO collimator.model: ONNX input projection: 43075 -> 9898 columns across 3 members
2026-11-06 20:54:58,146 INFO collimator.features: DB-backed feature extraction: 1444699 rows, 16 workers, batch_size=1024
2026-11-06 20:54:58,147 WARNING collimator.features: mem-aware workers: capping 16 -> 10 (headroom=42 GB after reserve=2 GB, per_worker=2.0 GB, shares=2); tune via COLLIMATOR_MEM_RESERVE_GB / COLLIMATOR_MEM_PER_WORKER_GB or disable with COLLIMATOR_MEM_AWARE_WORKERS=0
2026-11-06 20:54:58,147 INFO collimator.features: extraction worker budget: initial -> 10/16; preserving row order
2026-11-06 20:55:28,147 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=537111..542371; age=0.7s pending=10 completed_behind_head=0 admission=10; cgroup=9.40 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 20:55:28,148 INFO collimator.features: extraction worker budget: 10 -> 9/16; preserving row order
2026-11-06 20:55:29,066 INFO azoth_calibrate_ensemble: filegroups/filegroups_archive_oct26: extraction progress 23552/1444699 rows (1.6%), 9459400 nnz, 0.11 GiB written, 608.2 rows/s; last_row_id=542371
2026-11-06 20:55:58,147 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=1062290..1195340; age=25.6s pending=9 completed_behind_head=8 admission=9; cgroup=10.07 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 20:56:15,065 INFO azoth_calibrate_ensemble: filegroups/filegroups_archive_oct26: extraction progress 37888/1444699 rows (2.6%), 15182658 nnz, 0.17 GiB written, 447.2 rows/s; last_row_id=1195340
2026-11-06 20:56:28,148 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=1291676..1510314; age=4.6s pending=9 completed_behind_head=5 admission=9; cgroup=10.29 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 20:56:45,280 INFO azoth_calibrate_ensemble: filegroups/filegroups_archive_oct26: extraction progress 84992/1444699 rows (5.9%), 43482468 nnz, 0.49 GiB written, 739.5 rows/s; last_row_id=7902143
2026-11-06 20:56:58,148 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=8978405..9515791; age=16.9s pending=9 completed_behind_head=3 admission=9; cgroup=11.52 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 20:57:19,470 INFO azoth_calibrate_ensemble: filegroups/filegroups_archive_oct26: extraction progress 96256/1444699 rows (6.7%), 51600490 nnz, 0.58 GiB written, 645.5 rows/s; last_row_id=25583345
2026-11-06 20:57:28,149 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=25583377..52274300; age=27.7s pending=9 completed_behind_head=8 admission=9; cgroup=11.47 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 20:57:51,060 INFO azoth_calibrate_ensemble: filegroups/filegroups_archive_oct26: extraction progress 110592/1444699 rows (7.7%), 58523825 nnz, 0.66 GiB written, 612.0 rows/s; last_row_id=454153632
2026-11-06 20:57:58,149 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=454153773..454665085; age=23.3s pending=9 completed_behind_head=7 admission=9; cgroup=11.83 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 20:58:21,950 INFO azoth_calibrate_ensemble: filegroups/filegroups_archive_oct26: extraction progress 176128/1444699 rows (12.2%), 104593694 nnz, 1.17 GiB written, 832.3 rows/s; last_row_id=1149903775
2026-11-06 20:58:28,150 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=1165710963..1165729361; age=3.0s pending=9 completed_behind_head=0 admission=9; cgroup=12.60 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 20:58:58,150 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=1193205995..1198626196; age=14.7s pending=9 completed_behind_head=7 admission=9; cgroup=12.77 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 20:59:00,808 INFO azoth_calibrate_ensemble: filegroups/filegroups_archive_oct26: extraction progress 220160/1444699 rows (15.2%), 143006933 nnz, 1.60 GiB written, 879.0 rows/s; last_row_id=1198626196
2026-11-06 20:59:28,151 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=1330230621..1335248483; age=7.0s pending=9 completed_behind_head=0 admission=9; cgroup=13.10 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 20:59:31,814 INFO azoth_calibrate_ensemble: filegroups/filegroups_archive_oct26: extraction progress 249856/1444699 rows (17.3%), 167446236 nnz, 1.87 GiB written, 887.7 rows/s; last_row_id=1346379376
2026-11-06 20:59:58,152 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=1531530635..1534712374; age=19.6s pending=9 completed_behind_head=7 admission=9; cgroup=13.37 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 21:00:28,153 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=1531530635..1534712374; age=49.6s pending=9 completed_behind_head=8 admission=9; cgroup=13.35 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
make[1]: *** [Makefile:1258: azoth-calibrate] Terminated
/usr/lib/python3.14/multiprocessing/resource_tracker.py:475: UserWarning: resource_tracker: There appear to be 5 leaked semaphore objects to clean up at shutdown: {'/loky-822570-q210m8ta', '/loky-822570-hyqo4yxd', '/loky-822570-y5y3p7hz', '/loky-822570-6xiu5oy1', '/loky-822570-3xuvy3th'}
  warnings.warn()

## Gates

- **Confirm** (different seed, original profile): **PASS** — averaged 3-seed ensemble PR_AUC held: 0.9986 -> 0.9982; individual seeds may be noisy
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `87866efc2330c865` | `1ed6c3d710941b66` | `4639e2ac0d0c071d` |
| PR AUC | 0.9986 | 0.9982 | 0.9984 |
| ROC AUC | 0.9993 | 0.9993 | 0.9992 |
| F1 | 0.9875 | 0.9895 | 0.9867 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: signal: terminated (log /home/t/src/collimator/out/autocollie/runs/2026-11-06T19-56-14_20261106T195515-promote-87866efc2330c865_azoth-validate.log; tail: 2026-11-06 20:54:09,926 INFO collimator.model: ONNX input projection: 10252 -> 2023 columns across 3 members
2026-11-06 20:54:10,091 INFO collimator.features: DB-backed feature extraction: 13772 rows, 16 workers, batch_size=1024
2026-11-06 20:54:10,092 INFO collimator.features: mem-aware workers: 16 workers fit (headroom=42 GB after reserve=2 GB, per_worker=2.0 GB)
2026-11-06 20:54:10,092 INFO collimator.features: extraction worker budget: initial -> 16/16; preserving row order
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
2026-11-06 20:54:17,067 INFO collimator.matrix_store: disk-backed matrix ready: 13772 rows, 10440129 nnz, 0.12 GiB; scratch=/home/t/src/collimator/out/cache/matrix-scratch/matrix-zsvuy85h
2026-11-06 20:54:17,158 INFO azoth_calibrate_ensemble: filegroups/crx_selected: saved route feature matrix cache out/cache/azoth-route-features/filegroups_crx_selected-6641136469-7a599eb89e8c713a-1284d3d2472c4226.matrix.npz
2026-11-06 20:54:17,475 INFO azoth_calibrate_ensemble: filegroups/crx_selected: refreshed 13772 rows in 7.7s (fetch 0.1s, filter 0.0s, load 0.0s, extract 7.1s, matrix 0.0s, predict 0.1s, write 0.0s; feature_cache_read 0.0s, feature_cache_write 0.1s; features=10252 nnz=10440129)
2026-11-06 20:54:17,485 INFO azoth_calibrate_ensemble: scoring filegroups/data_recovery
2026-11-06 20:54:17,496 INFO azoth_calibrate_ensemble: filegroups/data_recovery: score identity changed; refreshing
2026-11-06 20:54:27,446 INFO collimator.model: ONNX input projection: 128071 -> 464 columns across 3 members
2026-11-06 20:54:28,976 INFO collimator.features: DB-backed feature extraction: 167978 rows, 16 workers, batch_size=1024
2026-11-06 20:54:28,977 INFO collimator.features: mem-aware workers: 16 workers fit (headroom=42 GB after reserve=2 GB, per_worker=2.0 GB)
2026-11-06 20:54:28,977 INFO collimator.features: extraction worker budget: initial -> 16/16; preserving row order
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
2026-11-06 20:54:43,878 INFO collimator.matrix_store: disk-backed matrix ready: 167978 rows, 6749983 nnz, 0.08 GiB; scratch=/home/t/src/collimator/out/cache/matrix-scratch/matrix-x2t3b0wy
2026-11-06 20:54:46,079 INFO azoth_calibrate_ensemble: filegroups/data_recovery: refreshed 167978 rows in 28.6s (fetch 9.9s, filter 0.0s, load 0.1s, extract 16.4s, matrix 0.0s, predict 1.0s, write 0.2s; feature_cache_read 0.0s, feature_cache_write 0.0s; features=128071 nnz=6749983)
2026-11-06 20:54:46,092 INFO azoth_calibrate_ensemble: scoring filegroups/filegroups_archive_oct26
2026-11-06 20:54:46,104 INFO azoth_calibrate_ensemble: filegroups/filegroups_archive_oct26: score identity changed; refreshing
2026-11-06 20:54:50,250 INFO collimator.model: ONNX input projection: 43075 -> 9898 columns across 3 members
2026-11-06 20:54:58,146 INFO collimator.features: DB-backed feature extraction: 1444699 rows, 16 workers, batch_size=1024
2026-11-06 20:54:58,147 WARNING collimator.features: mem-aware workers: capping 16 -> 10 (headroom=42 GB after reserve=2 GB, per_worker=2.0 GB, shares=2); tune via COLLIMATOR_MEM_RESERVE_GB / COLLIMATOR_MEM_PER_WORKER_GB or disable with COLLIMATOR_MEM_AWARE_WORKERS=0
2026-11-06 20:54:58,147 INFO collimator.features: extraction worker budget: initial -> 10/16; preserving row order
2026-11-06 20:55:28,147 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=537111..542371; age=0.7s pending=10 completed_behind_head=0 admission=10; cgroup=9.40 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 20:55:28,148 INFO collimator.features: extraction worker budget: 10 -> 9/16; preserving row order
2026-11-06 20:55:29,066 INFO azoth_calibrate_ensemble: filegroups/filegroups_archive_oct26: extraction progress 23552/1444699 rows (1.6%), 9459400 nnz, 0.11 GiB written, 608.2 rows/s; last_row_id=542371
2026-11-06 20:55:58,147 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=1062290..1195340; age=25.6s pending=9 completed_behind_head=8 admission=9; cgroup=10.07 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 20:56:15,065 INFO azoth_calibrate_ensemble: filegroups/filegroups_archive_oct26: extraction progress 37888/1444699 rows (2.6%), 15182658 nnz, 0.17 GiB written, 447.2 rows/s; last_row_id=1195340
2026-11-06 20:56:28,148 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=1291676..1510314; age=4.6s pending=9 completed_behind_head=5 admission=9; cgroup=10.29 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 20:56:45,280 INFO azoth_calibrate_ensemble: filegroups/filegroups_archive_oct26: extraction progress 84992/1444699 rows (5.9%), 43482468 nnz, 0.49 GiB written, 739.5 rows/s; last_row_id=7902143
2026-11-06 20:56:58,148 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=8978405..9515791; age=16.9s pending=9 completed_behind_head=3 admission=9; cgroup=11.52 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 20:57:19,470 INFO azoth_calibrate_ensemble: filegroups/filegroups_archive_oct26: extraction progress 96256/1444699 rows (6.7%), 51600490 nnz, 0.58 GiB written, 645.5 rows/s; last_row_id=25583345
2026-11-06 20:57:28,149 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=25583377..52274300; age=27.7s pending=9 completed_behind_head=8 admission=9; cgroup=11.47 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 20:57:51,060 INFO azoth_calibrate_ensemble: filegroups/filegroups_archive_oct26: extraction progress 110592/1444699 rows (7.7%), 58523825 nnz, 0.66 GiB written, 612.0 rows/s; last_row_id=454153632
2026-11-06 20:57:58,149 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=454153773..454665085; age=23.3s pending=9 completed_behind_head=7 admission=9; cgroup=11.83 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 20:58:21,950 INFO azoth_calibrate_ensemble: filegroups/filegroups_archive_oct26: extraction progress 176128/1444699 rows (12.2%), 104593694 nnz, 1.17 GiB written, 832.3 rows/s; last_row_id=1149903775
2026-11-06 20:58:28,150 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=1165710963..1165729361; age=3.0s pending=9 completed_behind_head=0 admission=9; cgroup=12.60 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 20:58:58,150 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=1193205995..1198626196; age=14.7s pending=9 completed_behind_head=7 admission=9; cgroup=12.77 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 20:59:00,808 INFO azoth_calibrate_ensemble: filegroups/filegroups_archive_oct26: extraction progress 220160/1444699 rows (15.2%), 143006933 nnz, 1.60 GiB written, 879.0 rows/s; last_row_id=1198626196
2026-11-06 20:59:28,151 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=1330230621..1335248483; age=7.0s pending=9 completed_behind_head=0 admission=9; cgroup=13.10 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 20:59:31,814 INFO azoth_calibrate_ensemble: filegroups/filegroups_archive_oct26: extraction progress 249856/1444699 rows (17.3%), 167446236 nnz, 1.87 GiB written, 887.7 rows/s; last_row_id=1346379376
2026-11-06 20:59:58,152 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=1531530635..1534712374; age=19.6s pending=9 completed_behind_head=7 admission=9; cgroup=13.37 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
2026-11-06 21:00:28,153 WARNING collimator.features: ordered extraction waiting: rows=1024 ids=1531530635..1534712374; age=49.6s pending=9 completed_behind_head=8 admission=9; cgroup=13.35 GiB memory_full_avg10=0.0% events={'low': 0, 'high': 3881, 'max': 0, 'oom': 0, 'oom_kill': 0, 'oom_group_kill': 0}
make[1]: *** [Makefile:1258: azoth-calibrate] Terminated
/usr/lib/python3.14/multiprocessing/resource_tracker.py:475: UserWarning: resource_tracker: There appear to be 5 leaked semaphore objects to clean up at shutdown: {'/loky-822570-q210m8ta', '/loky-822570-hyqo4yxd', '/loky-822570-y5y3p7hz', '/loky-822570-6xiu5oy1', '/loky-822570-3xuvy3th'}
  warnings.warn()
