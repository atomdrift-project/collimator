# Promote REJECTED — `c77ef0fd228cda8e` on `filetypes/jpeg`

Generated 2026-07-20T11:37:51Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-20T11-37-51_20260720T113746-promote-c77ef0fd228cda8e_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-c77ef0fd228cda8e/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-c77ef0fd228cda8e/general — bundle is incomplete
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9786)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `c77ef0fd228cda8e` | `9e139c4af0d7102d` | `b7bdf1a06814a002` |
| PR AUC | 0.9786 | 0.9783 | 0.9788 |
| ROC AUC | 0.9769 | 0.9766 | 0.9769 |
| F1 | 0.9425 | 0.9524 | 0.9535 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-20T11-37-51_20260720T113746-promote-c77ef0fd228cda8e_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-c77ef0fd228cda8e/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-c77ef0fd228cda8e/general — bundle is incomplete
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
