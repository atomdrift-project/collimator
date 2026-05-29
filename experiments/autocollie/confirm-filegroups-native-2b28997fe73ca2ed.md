# Confirm PASS — 2b28997fe73ca2ed on `filegroups/native`

Cycle `20260526T123338-confirm-2b28997fe73ca2ed` — 2026-05-26T12:33:38Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2b28997fe73ca2ed` | `2cd392f5c328b1fa` | `2cd392f5c328b1fa` | `2cd392f5c328b1fa` |
| PR AUC | 0.9995 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9995 | 1.0000 | 1.0000 | 0.9999 |
| Recall@3FPM | — | 0.8318 | 0.8821 | 0.8055 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2b28997fe73ca2ed
```
