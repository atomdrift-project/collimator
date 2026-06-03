# Promote REJECTED — `150007a00996c21d` on `filetypes/ole`

Generated 2026-06-03T16:34:24Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T16-34-24_20260603T163416-promote-150007a00996c21d_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-ole-150007a00996c21d/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-ole-150007a00996c21d/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9935)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `150007a00996c21d` | `a8ff612e51a38dea` | `49d10bdcd63b287c` |
| PR AUC | 0.9935 | 0.9935 | 0.9935 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 |
| F1 | 0.9967 | 0.9967 | 0.9967 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T16-34-24_20260603T163416-promote-150007a00996c21d_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-ole-150007a00996c21d/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-ole-150007a00996c21d/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
