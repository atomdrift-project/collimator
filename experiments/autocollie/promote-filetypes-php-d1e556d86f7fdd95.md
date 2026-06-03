# Promote REJECTED — `d1e556d86f7fdd95` on `filetypes/php`

Generated 2026-06-03T15:57:16Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T15-57-16_20260603T155632-promote-d1e556d86f7fdd95_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-php-d1e556d86f7fdd95/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-php-d1e556d86f7fdd95/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9958)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d1e556d86f7fdd95` | `36609aed60ec547a` | `cc4d104adf9802b5` |
| PR AUC | 0.9958 | 0.9960 | 0.9960 |
| ROC AUC | 0.9976 | 0.9977 | 0.9977 |
| F1 | 0.9808 | 0.9842 | 0.9851 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T15-57-16_20260603T155632-promote-d1e556d86f7fdd95_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-php-d1e556d86f7fdd95/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-php-d1e556d86f7fdd95/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
