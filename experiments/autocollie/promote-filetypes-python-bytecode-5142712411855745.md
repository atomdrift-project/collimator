# Promote REJECTED — `5142712411855745` on `filetypes/python-bytecode`

Generated 2026-06-03T15:55:00Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T15-54-59_20260603T155439-promote-5142712411855745_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-5142712411855745/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-5142712411855745/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9999)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `5142712411855745` | `190d312df14f6067` | `6a1895d7fed31c04` |
| PR AUC | 0.9999 | 0.9998 | 0.9998 |
| ROC AUC | 0.9996 | 0.9994 | 0.9995 |
| F1 | 0.9926 | 0.9912 | 0.9912 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T15-54-59_20260603T155439-promote-5142712411855745_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-5142712411855745/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-5142712411855745/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
