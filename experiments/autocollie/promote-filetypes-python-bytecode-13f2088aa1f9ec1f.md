# Promote REJECTED — `13f2088aa1f9ec1f` on `filetypes/python-bytecode`

Generated 2026-07-20T11:50:27Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-20T11-50-27_20260720T115012-promote-13f2088aa1f9ec1f_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-13f2088aa1f9ec1f/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-13f2088aa1f9ec1f/general — bundle is incomplete
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9961)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `13f2088aa1f9ec1f` | `4b5cc51b957c4d46` | `ad9e833ceeb71326` |
| PR AUC | 0.9961 | 0.9940 | 0.9948 |
| ROC AUC | 0.9987 | 0.9979 | 0.9982 |
| F1 | 0.9782 | 0.9843 | 0.9843 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-20T11-50-27_20260720T115012-promote-13f2088aa1f9ec1f_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-13f2088aa1f9ec1f/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-python-bytecode-13f2088aa1f9ec1f/general — bundle is incomplete
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
