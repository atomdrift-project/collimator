# Confirm PASS — f0cbfee378c5e461 on `filetypes/batch`

Cycle `20260608T111543-confirm-f0cbfee378c5e461` — 2026-06-08T11:15:43Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f0cbfee378c5e461` | `d7a0aa8715b1987c` | `d7a0aa8715b1987c` | `d7a0aa8715b1987c` |
| PR AUC | 0.9997 | 0.9996 | 0.9997 | 0.9997 |
| ROC AUC | 0.9973 | 0.9966 | 0.9974 | 0.9969 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f0cbfee378c5e461
```
