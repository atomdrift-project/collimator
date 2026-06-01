# Confirm PASS — fdb2f27d27404353 on `filetypes/zip`

Cycle `20260601T153030-confirm-fdb2f27d27404353` — 2026-06-01T15:30:30Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fdb2f27d27404353` | `b23741863e188363` | `b23741863e188363` | `b23741863e188363` |
| PR AUC | 0.9997 | 0.9996 | 0.9996 | 0.9995 |
| ROC AUC | 0.9963 | 0.9950 | 0.9948 | 0.9939 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=fdb2f27d27404353
```
