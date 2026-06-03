# Promote REJECTED — `9766143d6df5747f` on `filetypes/c`

Generated 2026-06-03T16:35:48Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T16-35-48_20260603T163530-promote-9766143d6df5747f_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-c-9766143d6df5747f/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-c-9766143d6df5747f/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9901)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `9766143d6df5747f` | `49db159864162d12` | `af51019ebeb9a7e1` |
| PR AUC | 0.9901 | 0.9899 | 0.9900 |
| ROC AUC | 0.9961 | 0.9960 | 0.9960 |
| F1 | 0.9439 | 0.9474 | 0.9485 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T16-35-48_20260603T163530-promote-9766143d6df5747f_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-c-9766143d6df5747f/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-c-9766143d6df5747f/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
