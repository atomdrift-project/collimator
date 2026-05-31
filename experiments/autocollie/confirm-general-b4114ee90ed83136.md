# Confirm PASS — b4114ee90ed83136 on `general`

Cycle `20260530T164549-confirm-b4114ee90ed83136` — 2026-05-30T16:45:49Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b4114ee90ed83136` | `0b9ba3ea014f6ca9` | `0b9ba3ea014f6ca9` | `0b9ba3ea014f6ca9` |
| PR AUC | 0.9988 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9988 | 0.9995 | 0.9995 | 0.9995 |
| Recall@3FPM | — | 0.5405 | 0.6747 | 0.6537 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b4114ee90ed83136
```
