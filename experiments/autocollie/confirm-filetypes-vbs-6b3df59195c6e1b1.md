# Confirm PASS — 6b3df59195c6e1b1 on `filetypes/vbs`

Cycle `20260609T072501-confirm-6b3df59195c6e1b1` — 2026-06-09T07:25:01Z

PR_AUC held across 3 seeds (orig 0.9967)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6b3df59195c6e1b1` | `6947bc7f7db13f86` | `6947bc7f7db13f86` | `6947bc7f7db13f86` |
| PR AUC | 0.9967 | 0.9967 | 0.9970 | 0.9969 |
| ROC AUC | 0.9887 | 0.9884 | 0.9897 | 0.9892 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6b3df59195c6e1b1
```
