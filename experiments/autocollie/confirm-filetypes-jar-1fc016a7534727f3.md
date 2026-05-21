# Confirm PASS — 1fc016a7534727f3 on `filetypes/jar`

Cycle `20260521T083526-confirm-1fc016a7534727f3` — 2026-05-21T08:35:26Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1fc016a7534727f3` | `7ef5d825f98d6ee2` | `7ef5d825f98d6ee2` | `7ef5d825f98d6ee2` |
| PR AUC | 0.9989 | 0.9976 | 0.9988 | 0.9979 |
| ROC AUC | 0.9980 | 0.9953 | 0.9978 | 0.9962 |
| Recall@3FPM | — | 0.8529 | 0.9176 | 0.8588 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1fc016a7534727f3
```
