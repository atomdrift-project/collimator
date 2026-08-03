# Confirm PASS — 8583bbaa51a0ee83 on `filetypes/ole`

Cycle `20260723T114239-confirm-8583bbaa51a0ee83` — 2026-07-23T11:42:39Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8583bbaa51a0ee83` | `5e3f0a84bf78bde4` | `5e3f0a84bf78bde4` | `5e3f0a84bf78bde4` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9990 | 0.9989 | 0.9989 | 0.9989 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8583bbaa51a0ee83
```
