# Confirm PASS — 12498240e9c38470 on `filetypes/zip`

Cycle `20260723T102504-confirm-12498240e9c38470` — 2026-07-23T10:25:04Z

PR_AUC held across 3 seeds (orig 0.9987)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `12498240e9c38470` | `ea75f9d0b0443c19` | `ea75f9d0b0443c19` | `ea75f9d0b0443c19` |
| PR AUC | 0.9987 | 0.9989 | 0.9990 | 0.9990 |
| ROC AUC | 0.9942 | 0.9953 | 0.9955 | 0.9956 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=12498240e9c38470
```
