# Promote REJECTED — `0b0cce45b1dcd49f` on `filegroups/scripts`

Generated 2026-06-03T16:33:46Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T16-33-46_20260603T162804-promote-0b0cce45b1dcd49f_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-0b0cce45b1dcd49f/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-0b0cce45b1dcd49f/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9978)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `0b0cce45b1dcd49f` | `a4335c4c7b950683` | `962d9427d4fae16b` |
| PR AUC | 0.9978 | 0.9991 | 0.9991 |
| ROC AUC | 0.9975 | 0.9989 | 0.9989 |
| F1 | 0.9763 | 0.9869 | 0.9864 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T16-33-46_20260603T162804-promote-0b0cce45b1dcd49f_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-0b0cce45b1dcd49f/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filegroups-scripts-0b0cce45b1dcd49f/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
