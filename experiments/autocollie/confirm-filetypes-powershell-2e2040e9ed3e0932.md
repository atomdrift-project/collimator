# Confirm PASS — 2e2040e9ed3e0932 on `filetypes/powershell`

Cycle `20260705T163403-confirm-2e2040e9ed3e0932` — 2026-07-05T16:34:03Z

PR_AUC held across 3 seeds (orig 0.9902)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2e2040e9ed3e0932` | `3efc865c683e1e07` | `3efc865c683e1e07` | `3efc865c683e1e07` |
| PR AUC | 0.9902 | 0.9903 | 0.9911 | 0.9895 |
| ROC AUC | 0.9837 | 0.9841 | 0.9852 | 0.9823 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2e2040e9ed3e0932
```
