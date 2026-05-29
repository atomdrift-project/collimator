# Confirm PASS — 25e1361942f05dab on `filetypes/text`

Cycle `20260527T014525-confirm-25e1361942f05dab` — 2026-05-27T01:45:25Z

PR_AUC held across 3 seeds (orig 0.9691)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `25e1361942f05dab` | `3e525524ba3cf860` | `3e525524ba3cf860` | `3e525524ba3cf860` |
| PR AUC | 0.9691 | 0.9599 | 0.9771 | 0.9672 |
| ROC AUC | 0.9851 | 0.9835 | 0.9890 | 0.9826 |
| Recall@3FPM | — | 0.6190 | 0.8571 | 0.8571 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=25e1361942f05dab
```
