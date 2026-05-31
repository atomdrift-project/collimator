# Confirm PASS — 0fe89239dc6c0da7 on `general`

Cycle `20260530T173356-confirm-0fe89239dc6c0da7` — 2026-05-30T17:33:56Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0fe89239dc6c0da7` | `30ba261668699265` | `30ba261668699265` | `30ba261668699265` |
| PR AUC | 0.9997 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9997 | 0.9996 | 0.9996 | 0.9996 |
| Recall@3FPM | — | 0.5862 | 0.5893 | 0.5590 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0fe89239dc6c0da7
```
