# Confirm PASS — 29b617ab57566236 on `filegroups/documents`

Cycle `20260804T230623-confirm-29b617ab57566236` — 2026-08-04T23:06:23Z

PR_AUC held across 3 seeds (orig 0.9746)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `29b617ab57566236` | `0f3ac753942251af` | `0f3ac753942251af` | `0f3ac753942251af` |
| PR AUC | 0.9746 | 0.9917 | 0.9943 | 0.9952 |
| ROC AUC | 0.9662 | 0.9762 | 0.9844 | 0.9868 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=29b617ab57566236
```
