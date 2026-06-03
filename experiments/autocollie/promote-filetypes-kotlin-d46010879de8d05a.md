# Promote REJECTED — `d46010879de8d05a` on `filetypes/kotlin`

Generated 2026-06-03T15:58:59Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T15-58-59_20260603T155811-promote-d46010879de8d05a_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-kotlin-d46010879de8d05a/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-kotlin-d46010879de8d05a/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9961)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `d46010879de8d05a` | `0084f0c35548775f` | `ed402ecf7d010cdd` |
| PR AUC | 0.9961 | 0.9997 | 0.9992 |
| ROC AUC | 0.8652 | 0.9791 | 0.9647 |
| F1 | 0.9928 | 0.9973 | 0.9953 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-06-03T15-58-59_20260603T155811-promote-d46010879de8d05a_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-kotlin-d46010879de8d05a/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-kotlin-d46010879de8d05a/general — bundle is incomplete
make[1]: *** [Makefile:1075: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
