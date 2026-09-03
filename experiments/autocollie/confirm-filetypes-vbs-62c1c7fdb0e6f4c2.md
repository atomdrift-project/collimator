# Confirm PASS — 62c1c7fdb0e6f4c2 on `filetypes/vbs`

Cycle `20260825T015441-confirm-62c1c7fdb0e6f4c2` — 2026-08-25T01:54:41Z

PR_AUC held across 3 seeds (orig 0.9991)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `62c1c7fdb0e6f4c2` | `6dd4672bc0c2006d` | `6dd4672bc0c2006d` | `6dd4672bc0c2006d` |
| PR AUC | 0.9991 | 0.9991 | 0.9992 | 0.9992 |
| ROC AUC | 0.9966 | 0.9967 | 0.9971 | 0.9971 |
| Recall@L50 | — | 0.9303 | 0.9303 | 0.9349 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=62c1c7fdb0e6f4c2
```
