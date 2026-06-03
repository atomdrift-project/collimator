# Promote REJECTED — `d3450ac06c22edfa` on `filegroups/portable`

Generated 2026-06-03T16:34:44Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T16-34-43_20260603T163434-promote-d3450ac06c22edfa_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filegroups-portable-d3450ac06c22edfa/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filegroups-portable-d3450ac06c22edfa/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9976)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d3450ac06c22edfa` | `50ff4d78f81f5c78` | `6b70a469b2316094` |
| PR AUC | 0.9976 | 0.9967 | 0.9972 |
| ROC AUC | 0.9996 | 0.9994 | 0.9995 |
| F1 | 0.9704 | 0.9738 | 0.9738 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T16-34-43_20260603T163434-promote-d3450ac06c22edfa_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filegroups-portable-d3450ac06c22edfa/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filegroups-portable-d3450ac06c22edfa/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
