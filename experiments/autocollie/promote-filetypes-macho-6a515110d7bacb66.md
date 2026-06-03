# Promote REJECTED — `6a515110d7bacb66` on `filetypes/macho`

Generated 2026-06-03T16:14:48Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T16-14-48_20260603T161323-promote-6a515110d7bacb66_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-macho-6a515110d7bacb66/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-macho-6a515110d7bacb66/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9966)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `6a515110d7bacb66` | `47ef7308185cf6bc` | `8f8c9fc6658842cb` |
| PR AUC | 0.9966 | 0.9960 | 0.9963 |
| ROC AUC | 0.9992 | 0.9990 | 0.9991 |
| F1 | 0.9701 | 0.9761 | 0.9747 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T16-14-48_20260603T161323-promote-6a515110d7bacb66_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-macho-6a515110d7bacb66/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-macho-6a515110d7bacb66/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
