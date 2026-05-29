# Confirm PASS — f3c965152d74c775 on `filegroups/media`

Cycle `20260527T004538-confirm-f3c965152d74c775` — 2026-05-27T00:45:38Z

PR_AUC held across 3 seeds (orig 0.9966)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f3c965152d74c775` | `1b59d29ee9688b38` | `1b59d29ee9688b38` | `1b59d29ee9688b38` |
| PR AUC | 0.9966 | 0.9944 | 0.9927 | 0.9964 |
| ROC AUC | 0.9959 | 0.9931 | 0.9909 | 0.9957 |
| Recall@3FPM | — | 0.9000 | 0.8778 | 0.9000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f3c965152d74c775
```
