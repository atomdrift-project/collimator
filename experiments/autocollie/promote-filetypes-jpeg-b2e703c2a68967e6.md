# Promote REJECTED — `b2e703c2a68967e6` on `filetypes/jpeg`

Generated 2026-06-02T03:16:10Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-02T03-16-10_20260602T031608-promote-b2e703c2a68967e6_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-b2e703c2a68967e6/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-b2e703c2a68967e6/general — bundle is incomplete
make[1]: *** [Makefile:1052: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9460)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `b2e703c2a68967e6` | `561e114edbec5220` | `524487ce760731ac` |
| PR AUC | 0.9460 | 0.9787 | 0.9797 |
| ROC AUC | 0.9687 | 0.9887 | 0.9890 |
| F1 | 0.8451 | 0.9231 | 0.9114 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-02T03-16-10_20260602T031608-promote-b2e703c2a68967e6_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-b2e703c2a68967e6/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-jpeg-b2e703c2a68967e6/general — bundle is incomplete
make[1]: *** [Makefile:1052: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
