# Promote REJECTED — `858bf84f98b417e2` on `filetypes/shell`

Generated 2026-06-03T16:37:05Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T16-37-05_20260603T163626-promote-858bf84f98b417e2_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-shell-858bf84f98b417e2/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-shell-858bf84f98b417e2/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9991)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `858bf84f98b417e2` | `6cdfa949aa04a7e6` | `81d91cbb1ecad19e` |
| PR AUC | 0.9991 | 0.9992 | 0.9992 |
| ROC AUC | 0.9991 | 0.9992 | 0.9992 |
| F1 | 0.9802 | 0.9802 | 0.9782 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T16-37-05_20260603T163626-promote-858bf84f98b417e2_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-shell-858bf84f98b417e2/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-shell-858bf84f98b417e2/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
