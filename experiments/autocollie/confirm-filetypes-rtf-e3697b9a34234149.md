# Confirm PASS — e3697b9a34234149 on `filetypes/rtf`

Cycle `20261102T223617-confirm-e3697b9a34234149` — 2026-11-02T22:36:17Z

averaged 3-seed ensemble PR_AUC held: 0.9985 -> 0.9993; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e3697b9a34234149` | `1bd15e72d9206a2e` | `1bd15e72d9206a2e` | `1bd15e72d9206a2e` |
| PR AUC | 0.9985 | 0.9985 | 0.9977 | 0.9993 |
| ROC AUC | 0.9949 | 0.9949 | 0.9919 | 0.9969 |
| Recall@L50 | — | 0.9899 | 0.9435 | 0.9849 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e3697b9a34234149
```
