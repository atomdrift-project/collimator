# Promote REJECTED — `3777e577d3f30f3d` on `filetypes/vbs`

Generated 2026-06-03T16:35:10Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T16-35-10_20260603T163457-promote-3777e577d3f30f3d_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-3777e577d3f30f3d/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-3777e577d3f30f3d/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9995)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `3777e577d3f30f3d` | `c7508b5ef823ae90` | `ab23df179a3a2120` |
| PR AUC | 0.9995 | 0.9995 | 0.9996 |
| ROC AUC | 0.9898 | 0.9898 | 0.9904 |
| F1 | 0.9930 | 0.9926 | 0.9930 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T16-35-10_20260603T163457-promote-3777e577d3f30f3d_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-3777e577d3f30f3d/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-vbs-3777e577d3f30f3d/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
