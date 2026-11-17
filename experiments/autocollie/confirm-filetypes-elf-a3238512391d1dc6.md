# Confirm PASS — a3238512391d1dc6 on `filetypes/elf`

Cycle `20261114T173855-confirm-a3238512391d1dc6` — 2026-11-14T17:38:55Z

averaged 3-seed ensemble PR_AUC held: 0.9999 -> 1.0000; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a3238512391d1dc6` | `9cc7dc985ea83efa` | `9cc7dc985ea83efa` | `9cc7dc985ea83efa` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9999 | 1.0000 | 1.0000 | 1.0000 |
| Recall@L50 | — | 0.9892 | 0.9864 | 0.9910 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a3238512391d1dc6
```
