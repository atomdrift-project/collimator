# Promote REJECTED — `10ebdf856e9f110f` on `filetypes/jpeg`

Generated 2026-07-13T21:44:11Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-13T21-44-11_20260713T214403-promote-10ebdf856e9f110f_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-10ebdf856e9f110f/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-10ebdf856e9f110f/general — bundle is incomplete
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9768)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `10ebdf856e9f110f` | `b08d22467a8b67f7` | `a6c562bcc8430cf3` |
| PR AUC | 0.9768 | 0.9774 | 0.9761 |
| ROC AUC | 0.9755 | 0.9776 | 0.9762 |
| F1 | 0.8378 | 0.9647 | 0.9535 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-13T21-44-11_20260713T214403-promote-10ebdf856e9f110f_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-10ebdf856e9f110f/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-10ebdf856e9f110f/general — bundle is incomplete
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
