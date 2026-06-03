# Promote REJECTED — `ec8d6fc93e024550` on `filetypes/batch`

Generated 2026-06-03T16:16:30Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T16-16-30_20260603T161613-promote-ec8d6fc93e024550_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-batch-ec8d6fc93e024550/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-batch-ec8d6fc93e024550/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9998)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `ec8d6fc93e024550` | `a41fc92b01a0341c` | `cffa91e669705263` |
| PR AUC | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9978 | 0.9979 | 0.9977 |
| F1 | 0.9922 | 0.9929 | 0.9909 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T16-16-30_20260603T161613-promote-ec8d6fc93e024550_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-batch-ec8d6fc93e024550/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-batch-ec8d6fc93e024550/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
