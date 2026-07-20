# Promote REJECTED — `75895df7f854c7cb` on `filetypes/java_class`

Generated 2026-07-20T11:42:41Z

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-20T11-42-41_20260720T114158-promote-75895df7f854c7cb_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-75895df7f854c7cb/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-75895df7f854c7cb/general — bundle is incomplete
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')

## Gates

- **Confirm** (different seed, original profile): **PASS** — PR_AUC held across 3 seeds (orig 0.9905)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `75895df7f854c7cb` | `c9488885127e4a4a` | `1a897ad519e75816` |
| PR AUC | 0.9905 | 0.9902 | 0.9906 |
| ROC AUC | 0.9987 | 0.9987 | 0.9988 |
| F1 | 0.9484 | 0.9531 | 0.9510 |

## Disposition

This spec did not survive the promotion ladder.

azoth-validate failed: exit status 2 (log /home/t/collimator/out/autocollie/runs/2026-07-20T11-42-41_20260720T114158-promote-75895df7f854c7cb_azoth-validate.log; tail: make[1]: Entering directory '/home/t/collimator'
azoth-calibrate: /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-75895df7f854c7cb/general/threshold_scores.npz missing AND no general model found in /home/t/collimator/out/models/azoth-candidate-filetypes-java_class-75895df7f854c7cb/general — bundle is incomplete
make[1]: *** [Makefile:1253: azoth-calibrate] Error 1
make[1]: Leaving directory '/home/t/collimator')
