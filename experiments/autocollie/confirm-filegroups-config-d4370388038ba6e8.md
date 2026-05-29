# Confirm PASS — d4370388038ba6e8 on `filegroups/config`

Cycle `20260525T191618-confirm-d4370388038ba6e8` — 2026-05-25T19:16:18Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d4370388038ba6e8` | `c4374c8fcf8580b0` | `c4374c8fcf8580b0` | `c4374c8fcf8580b0` |
| PR AUC | 0.9997 | 0.9997 | 0.9997 | 0.9997 |
| ROC AUC | 0.9995 | 0.9994 | 0.9994 | 0.9995 |
| Recall@3FPM | — | 0.9261 | 0.9400 | 0.9535 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d4370388038ba6e8
```
