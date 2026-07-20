# Promote REJECTED — `99c28854e55f4b8b` on `filetypes/xlsx`

Generated 2026-07-20T11:30:14Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-20T11-30-14_20260720T113001-promote-99c28854e55f4b8b_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-99c28854e55f4b8b/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-99c28854e55f4b8b/general — bundle is incomplete
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9953)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `99c28854e55f4b8b` | `9770c8db23ec9109` | `4e4c1b5cd058061e` |
| PR AUC | 0.9953 | 0.9953 | 0.9953 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 |
| F1 | 0.9977 | 0.9977 | 0.9977 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-20T11-30-14_20260720T113001-promote-99c28854e55f4b8b_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-99c28854e55f4b8b/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-99c28854e55f4b8b/general — bundle is incomplete
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
