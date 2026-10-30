# Confirm PASS — 4fc28bd9683ad39e on `filetypes/zip`

Cycle `20261030T193303-confirm-4fc28bd9683ad39e` — 2026-10-30T19:33:03Z

averaged 3-seed ensemble PR_AUC held: 0.9978 -> 0.9985; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4fc28bd9683ad39e` | `bedf3c5bcd062bbd` | `bedf3c5bcd062bbd` | `bedf3c5bcd062bbd` |
| PR AUC | 0.9978 | 0.9985 | 0.9984 | 0.9984 |
| ROC AUC | 0.9977 | 0.9984 | 0.9983 | 0.9983 |
| Recall@L50 | — | 0.7510 | 0.5723 | 0.5886 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4fc28bd9683ad39e
```
