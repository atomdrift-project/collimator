# Promote REJECTED — `a1f5571d9296f591` on `filetypes/jpeg`

Generated 2026-06-02T03:07:49Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-02T03-07-49_20260602T030744-promote-a1f5571d9296f591_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-a1f5571d9296f591/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-a1f5571d9296f591/general — bundle is incomplete
make[1]: *** [Makefile:1052: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9399)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `a1f5571d9296f591` | `0ecdd05ad39583e1` | `3c0e55e14ba8a5d3` |
| PR AUC | 0.9399 | 0.9716 | 0.9564 |
| ROC AUC | 0.9683 | 0.9851 | 0.9777 |
| F1 | 0.8831 | 0.9114 | 0.9000 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-02T03-07-49_20260602T030744-promote-a1f5571d9296f591_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-a1f5571d9296f591/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-a1f5571d9296f591/general — bundle is incomplete
make[1]: *** [Makefile:1052: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
