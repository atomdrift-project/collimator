# Confirm PASS — b273e47b007fde3a on `filetypes/jar`

Cycle `20260718T140245-confirm-b273e47b007fde3a` — 2026-07-18T14:02:45Z

PR_AUC held across 3 seeds (orig 0.9855)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b273e47b007fde3a` | `4c80776b54d2751b` | `4c80776b54d2751b` | `4c80776b54d2751b` |
| PR AUC | 0.9855 | 0.9860 | 0.9854 | 0.9805 |
| ROC AUC | 0.9849 | 0.9858 | 0.9847 | 0.9797 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b273e47b007fde3a
```
