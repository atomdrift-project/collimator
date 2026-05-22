# Confirm PASS — 71c410fd6dae113a on `filetypes/c`

Cycle `20260522T171041-confirm-71c410fd6dae113a` — 2026-05-22T17:10:41Z

PR_AUC held across 3 seeds (orig 0.9922)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `71c410fd6dae113a` | `6b5e8ecc60f38fd9` | `6b5e8ecc60f38fd9` | `6b5e8ecc60f38fd9` |
| PR AUC | 0.9922 | 0.9921 | 0.9917 | 0.9919 |
| ROC AUC | 0.9959 | 0.9959 | 0.9956 | 0.9957 |
| Recall@3FPM | — | 0.7865 | 0.8190 | 0.8028 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=71c410fd6dae113a
```
