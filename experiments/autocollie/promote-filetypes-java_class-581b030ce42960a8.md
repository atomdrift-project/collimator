# Promote REJECTED — `581b030ce42960a8` on `filetypes/java_class`

Generated 2026-06-03T15:54:22Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T15-54-22_20260603T155353-promote-581b030ce42960a8_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-581b030ce42960a8/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-581b030ce42960a8/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9970)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `581b030ce42960a8` | `09dbc099bd16c40d` | `80cf3abc615f0334` |
| PR AUC | 0.9970 | 0.9960 | 0.9966 |
| ROC AUC | 0.9995 | 0.9993 | 0.9994 |
| F1 | 0.9624 | 0.9764 | 0.9738 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T15-54-22_20260603T155353-promote-581b030ce42960a8_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-581b030ce42960a8/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-581b030ce42960a8/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
