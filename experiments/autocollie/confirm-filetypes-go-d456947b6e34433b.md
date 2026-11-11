# Confirm PASS — d456947b6e34433b on `filetypes/go`

Cycle `20261110T194859-confirm-d456947b6e34433b` — 2026-11-10T19:48:59Z

averaged 3-seed ensemble PR_AUC held: 0.9316 -> 0.9413; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d456947b6e34433b` | `95c551f107a3c971` | `95c551f107a3c971` | `95c551f107a3c971` |
| PR AUC | 0.9316 | 0.9357 | 0.9367 | 0.9354 |
| ROC AUC | 0.9742 | 0.9782 | 0.9791 | 0.9784 |
| Recall@L50 | — | 0.6237 | 0.6392 | 0.6400 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d456947b6e34433b
```
