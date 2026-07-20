# Promote REJECTED — `edaddafe996f16a5` on `filetypes/makefile`

Generated 2026-07-20T11:29:12Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-20T11-29-12_20260720T112906-promote-edaddafe996f16a5_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-edaddafe996f16a5/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-edaddafe996f16a5/general — bundle is incomplete
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.4306)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `edaddafe996f16a5` | `af3e2f07e7483e2a` | `a5c57a335ca03889` |
| PR AUC | 0.4306 | 0.8093 | 0.7659 |
| ROC AUC | 0.8594 | 0.9639 | 0.9699 |
| F1 | 0.6154 | 0.8000 | 0.6667 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-20T11-29-12_20260720T112906-promote-edaddafe996f16a5_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-edaddafe996f16a5/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-makefile-edaddafe996f16a5/general — bundle is incomplete
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
