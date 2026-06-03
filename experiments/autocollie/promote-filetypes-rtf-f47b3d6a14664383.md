# Promote REJECTED — `f47b3d6a14664383` on `filetypes/rtf`

Generated 2026-06-03T15:53:30Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T15-53-29_20260603T155313-promote-f47b3d6a14664383_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-rtf-f47b3d6a14664383/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-rtf-f47b3d6a14664383/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9946)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `f47b3d6a14664383` | `67be8692da558f25` | `c48fe2bb76e1cd21` |
| PR AUC | 0.9946 | 0.9946 | 0.9946 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 |
| F1 | 0.9973 | 0.9973 | 0.9973 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T15-53-29_20260603T155313-promote-f47b3d6a14664383_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-rtf-f47b3d6a14664383/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-rtf-f47b3d6a14664383/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
