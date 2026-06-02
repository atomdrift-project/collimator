# Promote REJECTED — `45828fa044b15223` on `filetypes/jpeg`

Generated 2026-06-02T02:49:56Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-02T02-49-56_20260602T024953-promote-45828fa044b15223_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-45828fa044b15223/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-45828fa044b15223/general — bundle is incomplete
make[1]: *** [Makefile:1052: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9407)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `45828fa044b15223` | `82b989fca3354578` | `5808d51118a33ea3` |
| PR AUC | 0.9407 | 0.9599 | 0.9407 |
| ROC AUC | 0.9691 | 0.9785 | 0.9691 |
| F1 | 0.8780 | 0.9000 | 0.8780 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-02T02-49-56_20260602T024953-promote-45828fa044b15223_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-45828fa044b15223/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-45828fa044b15223/general — bundle is incomplete
make[1]: *** [Makefile:1052: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
