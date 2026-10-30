# Promote REJECTED — `3ec2962c2bf168cd` on `filetypes/pe`

Generated 2026-10-30T19:16:24Z

confirm did not hold: experiment failed: timed out after 1h30m0s (timeout(1) exit 124)
--- experiment log tail ---
...(truncated)...
.features: trigram selection complete: 4096 shortlist candidates tested, 500 selected, 1 rounds, exhaustive fallback=False
15:09:36 INFO  collimator.features: extended metrics: 177 keys from 5000 scanned rows (always-keep below threshold: ast_depth_capped)
15:09:44 INFO  collimator.features: crit-category n-grams: 59 unigrams, 500 bigrams, 500 trigrams from 5000 scanned rows
15:10:02 INFO  collimator.features: ATT&CK/MBC n-grams: 500/500 atk bi/tri, 500/500 mbc bi/tri from 5000 scanned rows
15:10:02 INFO  collimator.features: feature vocabulary: 74282 columns (no fixed name filter)
15:10:02 INFO  collimator.features: vocab: 1546 paths, 113 filetypes, 28600 elements, 5000 bigrams, 1 ghosts, 177 ext_metrics -> 74282 features
15:10:02 INFO  collimator.features: saved feature spec: 74282 features to out/cache/experiment/azoth/vocabulary_99282a308e3a01015fa6e0b9d03994c5320d9f1c03af23e801387c4356d6a8fe/feature_spec.tmp
15:10:03 INFO  collimator.experiment: pass 2: extracting all features (worker-local DB fetching)
15:10:03 WARNING collimator.features: mem-aware workers: capping 64 -> 37 (headroom=75 GB after reserve=48 GB, per_worker=2.0 GB); tune via COLLIMATOR_MEM_RESERVE_GB / COLLIMATOR_MEM_PER_WORKER_GB or disable with COLLIMATOR_MEM_AWARE_WORKERS=0
15:10:03 INFO  collimator.features: mem-aware workers: 37 workers fit (headroom=76 GB after reserve=48 GB, per_worker=2.0 GB)
15:10:03 INFO  collimator.features: extraction worker budget: initial -> 37/37; preserving row order
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
15:10:33 INFO  collimator.features: extraction worker budget: 37 -> 31/37; preserving row order
15:11:03 INFO  collimator.features: extraction worker budget: 31 -> 32/37; preserving row order
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
15:11:33 INFO  collimator.features: extraction worker budget: 32 -> 31/37; preserving row order
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
15:12:33 INFO  collimator.features: extraction worker budget: 31 -> 30/37; preserving row order
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
15:13:03 INFO  collimator.features: extraction worker budget: 30 -> 24/37; preserving row order
15:13:33 INFO  collimator.features: extraction worker budget: 24 -> 25/37; preserving row order
15:14:03 INFO  collimator.features: extraction worker budget: 25 -> 27/37; preserving row order
15:14:33 INFO  collimator.features: extraction worker budget: 27 -> 29/37; preserving row order
15:15:03 INFO  collimator.features: extraction worker budget: 29 -> 33/37; preserving row order
make[1]: *** [Makefile:2122: experiment] Terminated
--- end log tail ---
full log: /home/t/src/collimator/out/autocollie/runs/2026-10-30T17-46-24_20261030T174253-confirm-3ec2962c2bf168cd_pe_hardneg_fine_sweep_confirm_seedsearch_3.log

## Gates

- **Confirm** (different seed, original profile): **FAIL** — experiment failed: timed out after 1h30m0s (timeout(1) exit 124)
--- experiment log tail ---
...(truncated)...
.features: trigram selection complete: 4096 shortlist candidates tested, 500 selected, 1 rounds, exhaustive fallback=False
15:09:36 INFO  collimator.features: extended metrics: 177 keys from 5000 scanned rows (always-keep below threshold: ast_depth_capped)
15:09:44 INFO  collimator.features: crit-category n-grams: 59 unigrams, 500 bigrams, 500 trigrams from 5000 scanned rows
15:10:02 INFO  collimator.features: ATT&CK/MBC n-grams: 500/500 atk bi/tri, 500/500 mbc bi/tri from 5000 scanned rows
15:10:02 INFO  collimator.features: feature vocabulary: 74282 columns (no fixed name filter)
15:10:02 INFO  collimator.features: vocab: 1546 paths, 113 filetypes, 28600 elements, 5000 bigrams, 1 ghosts, 177 ext_metrics -> 74282 features
15:10:02 INFO  collimator.features: saved feature spec: 74282 features to out/cache/experiment/azoth/vocabulary_99282a308e3a01015fa6e0b9d03994c5320d9f1c03af23e801387c4356d6a8fe/feature_spec.tmp
15:10:03 INFO  collimator.experiment: pass 2: extracting all features (worker-local DB fetching)
15:10:03 WARNING collimator.features: mem-aware workers: capping 64 -> 37 (headroom=75 GB after reserve=48 GB, per_worker=2.0 GB); tune via COLLIMATOR_MEM_RESERVE_GB / COLLIMATOR_MEM_PER_WORKER_GB or disable with COLLIMATOR_MEM_AWARE_WORKERS=0
15:10:03 INFO  collimator.features: mem-aware workers: 37 workers fit (headroom=76 GB after reserve=48 GB, per_worker=2.0 GB)
15:10:03 INFO  collimator.features: extraction worker budget: initial -> 37/37; preserving row order
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
15:10:33 INFO  collimator.features: extraction worker budget: 37 -> 31/37; preserving row order
15:11:03 INFO  collimator.features: extraction worker budget: 31 -> 32/37; preserving row order
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
15:11:33 INFO  collimator.features: extraction worker budget: 32 -> 31/37; preserving row order
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
15:12:33 INFO  collimator.features: extraction worker budget: 31 -> 30/37; preserving row order
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
15:13:03 INFO  collimator.features: extraction worker budget: 30 -> 24/37; preserving row order
15:13:33 INFO  collimator.features: extraction worker budget: 24 -> 25/37; preserving row order
15:14:03 INFO  collimator.features: extraction worker budget: 25 -> 27/37; preserving row order
15:14:33 INFO  collimator.features: extraction worker budget: 27 -> 29/37; preserving row order
15:15:03 INFO  collimator.features: extraction worker budget: 29 -> 33/37; preserving row order
make[1]: *** [Makefile:2122: experiment] Terminated
--- end log tail ---
full log: /home/t/src/collimator/out/autocollie/runs/2026-10-30T17-46-24_20261030T174253-confirm-3ec2962c2bf168cd_pe_hardneg_fine_sweep_confirm_seedsearch_3.log
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `3ec2962c2bf168cd` | `` | `—` |
| PR AUC | 0.9992 | — | — |
| ROC AUC | 0.9992 | — | — |
| F1 | 0.9885 | — | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: experiment failed: timed out after 1h30m0s (timeout(1) exit 124)
--- experiment log tail ---
...(truncated)...
.features: trigram selection complete: 4096 shortlist candidates tested, 500 selected, 1 rounds, exhaustive fallback=False
15:09:36 INFO  collimator.features: extended metrics: 177 keys from 5000 scanned rows (always-keep below threshold: ast_depth_capped)
15:09:44 INFO  collimator.features: crit-category n-grams: 59 unigrams, 500 bigrams, 500 trigrams from 5000 scanned rows
15:10:02 INFO  collimator.features: ATT&CK/MBC n-grams: 500/500 atk bi/tri, 500/500 mbc bi/tri from 5000 scanned rows
15:10:02 INFO  collimator.features: feature vocabulary: 74282 columns (no fixed name filter)
15:10:02 INFO  collimator.features: vocab: 1546 paths, 113 filetypes, 28600 elements, 5000 bigrams, 1 ghosts, 177 ext_metrics -> 74282 features
15:10:02 INFO  collimator.features: saved feature spec: 74282 features to out/cache/experiment/azoth/vocabulary_99282a308e3a01015fa6e0b9d03994c5320d9f1c03af23e801387c4356d6a8fe/feature_spec.tmp
15:10:03 INFO  collimator.experiment: pass 2: extracting all features (worker-local DB fetching)
15:10:03 WARNING collimator.features: mem-aware workers: capping 64 -> 37 (headroom=75 GB after reserve=48 GB, per_worker=2.0 GB); tune via COLLIMATOR_MEM_RESERVE_GB / COLLIMATOR_MEM_PER_WORKER_GB or disable with COLLIMATOR_MEM_AWARE_WORKERS=0
15:10:03 INFO  collimator.features: mem-aware workers: 37 workers fit (headroom=76 GB after reserve=48 GB, per_worker=2.0 GB)
15:10:03 INFO  collimator.features: extraction worker budget: initial -> 37/37; preserving row order
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
15:10:33 INFO  collimator.features: extraction worker budget: 37 -> 31/37; preserving row order
15:11:03 INFO  collimator.features: extraction worker budget: 31 -> 32/37; preserving row order
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
15:11:33 INFO  collimator.features: extraction worker budget: 32 -> 31/37; preserving row order
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
15:12:33 INFO  collimator.features: extraction worker budget: 31 -> 30/37; preserving row order
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
fact profile azoth-1fbfcdb8a8ed5902 does not cover this feature layout; keeping the sample and using available facts with the usual defaults for absent inputs
15:13:03 INFO  collimator.features: extraction worker budget: 30 -> 24/37; preserving row order
15:13:33 INFO  collimator.features: extraction worker budget: 24 -> 25/37; preserving row order
15:14:03 INFO  collimator.features: extraction worker budget: 25 -> 27/37; preserving row order
15:14:33 INFO  collimator.features: extraction worker budget: 27 -> 29/37; preserving row order
15:15:03 INFO  collimator.features: extraction worker budget: 29 -> 33/37; preserving row order
make[1]: *** [Makefile:2122: experiment] Terminated
--- end log tail ---
full log: /home/t/src/collimator/out/autocollie/runs/2026-10-30T17-46-24_20261030T174253-confirm-3ec2962c2bf168cd_pe_hardneg_fine_sweep_confirm_seedsearch_3.log
