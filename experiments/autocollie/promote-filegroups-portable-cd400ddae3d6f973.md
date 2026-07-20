# Promote REJECTED — `cd400ddae3d6f973` on `filegroups/portable`

Generated 2026-07-13T21:47:38Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-13T21-47-38_20260713T214644-promote-cd400ddae3d6f973_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filegroups-portable-cd400ddae3d6f973/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filegroups-portable-cd400ddae3d6f973/general — bundle is incomplete
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9947)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `cd400ddae3d6f973` | `908f1b67f7580a83` | `2b4ab189cc59f82b` |
| PR AUC | 0.9947 | 0.9936 | 0.9940 |
| ROC AUC | 0.9987 | 0.9981 | 0.9982 |
| F1 | 0.9666 | 0.9716 | 0.9726 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-13T21-47-38_20260713T214644-promote-cd400ddae3d6f973_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filegroups-portable-cd400ddae3d6f973/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filegroups-portable-cd400ddae3d6f973/general — bundle is incomplete
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
