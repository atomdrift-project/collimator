# Confirm PASS — 076145546b051bf2 on `filetypes/xml`

Cycle `20260628T154606-confirm-076145546b051bf2` — 2026-06-28T15:46:06Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `076145546b051bf2` | `719b9ad61176fa84` | `719b9ad61176fa84` | `719b9ad61176fa84` |
| PR AUC | 0.9995 | 1.0000 | 1.0000 | 0.9995 |
| ROC AUC | 0.9999 | 1.0000 | 1.0000 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=076145546b051bf2
```
