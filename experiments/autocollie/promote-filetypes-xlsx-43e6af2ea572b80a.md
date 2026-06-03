# Promote REJECTED — `43e6af2ea572b80a` on `filetypes/xlsx`

Generated 2026-06-03T16:34:08Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T16-34-08_20260603T163358-promote-43e6af2ea572b80a_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-43e6af2ea572b80a/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-43e6af2ea572b80a/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9974)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `43e6af2ea572b80a` | `1c03c3ae4abc7fe3` | `90264b42c691309f` |
| PR AUC | 0.9974 | 0.9974 | 0.9974 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 |
| F1 | 0.9987 | 0.9987 | 0.9987 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T16-34-08_20260603T163358-promote-43e6af2ea572b80a_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-43e6af2ea572b80a/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-xlsx-43e6af2ea572b80a/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
