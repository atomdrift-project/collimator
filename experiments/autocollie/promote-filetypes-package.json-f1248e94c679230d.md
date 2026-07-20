# Promote REJECTED — `f1248e94c679230d` on `filetypes/package.json`

Generated 2026-07-20T11:48:45Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-20T11-48-45_20260720T114825-promote-f1248e94c679230d_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-package.json-f1248e94c679230d/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-package.json-f1248e94c679230d/general — bundle is incomplete
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9981)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `f1248e94c679230d` | `0fa466c29b4bb754` | `3b1c773e647635f0` |
| PR AUC | 0.9981 | 0.9983 | 0.9984 |
| ROC AUC | 0.9984 | 0.9985 | 0.9985 |
| F1 | 0.9921 | 0.9923 | 0.9923 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-20T11-48-45_20260720T114825-promote-f1248e94c679230d_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-package.json-f1248e94c679230d/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-package.json-f1248e94c679230d/general — bundle is incomplete
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
