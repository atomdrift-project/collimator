# Confirm PASS — d9d557086e637153 on `filegroups/source`

Cycle `20260601T140508-confirm-d9d557086e637153` — 2026-06-01T14:05:08Z

PR_AUC held across 3 seeds (orig 0.9991)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d9d557086e637153` | `267a0484c2a4a6f9` | `267a0484c2a4a6f9` | `267a0484c2a4a6f9` |
| PR AUC | 0.9991 | 0.9989 | 0.9989 | 0.9989 |
| ROC AUC | 0.9984 | 0.9982 | 0.9982 | 0.9982 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d9d557086e637153
```
