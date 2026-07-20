# Promote REJECTED — `e6bb2d67ca118174` on `filetypes/whl`

Generated 2026-07-20T11:37:29Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-20T11-37-29_20260720T113606-promote-e6bb2d67ca118174_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-whl-e6bb2d67ca118174/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-whl-e6bb2d67ca118174/general — bundle is incomplete
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9666)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `e6bb2d67ca118174` | `94749e446015336e` | `2e0e3511d2c1f4d8` |
| PR AUC | 0.9666 | 0.9684 | 0.9679 |
| ROC AUC | 0.9635 | 0.9685 | 0.9661 |
| F1 | 0.9166 | 0.9199 | 0.9157 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-20T11-37-29_20260720T113606-promote-e6bb2d67ca118174_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-whl-e6bb2d67ca118174/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-whl-e6bb2d67ca118174/general — bundle is incomplete
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
