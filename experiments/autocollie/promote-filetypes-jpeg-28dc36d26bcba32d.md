# Promote REJECTED — `28dc36d26bcba32d` on `filetypes/jpeg`

Generated 2026-06-02T02:32:08Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-02T02-32-08_20260602T023202-promote-28dc36d26bcba32d_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-28dc36d26bcba32d/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-28dc36d26bcba32d/general — bundle is incomplete
make[1]: *** [Makefile:1052: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9697)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `28dc36d26bcba32d` | `192d201966a81720` | `d3ea4cde5a8c6e57` |
| PR AUC | 0.9697 | 0.9851 | 0.9801 |
| ROC AUC | 0.9840 | 0.9922 | 0.9894 |
| F1 | 0.8358 | 0.9351 | 0.9351 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-02T02-32-08_20260602T023202-promote-28dc36d26bcba32d_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-28dc36d26bcba32d/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-28dc36d26bcba32d/general — bundle is incomplete
make[1]: *** [Makefile:1052: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
