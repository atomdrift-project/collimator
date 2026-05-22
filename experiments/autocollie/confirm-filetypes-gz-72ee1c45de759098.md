# Confirm PASS — 72ee1c45de759098 on `filetypes/gz`

Cycle `20260522T173351-confirm-72ee1c45de759098` — 2026-05-22T17:33:51Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `72ee1c45de759098` | `d75378540711b47e` | `d75378540711b47e` | `d75378540711b47e` |
| PR AUC | 0.9988 | 0.9988 | 0.9990 | 0.9992 |
| ROC AUC | 0.9985 | 0.9985 | 0.9987 | 0.9989 |
| Recall@3FPM | — | 0.9912 | 0.9912 | 0.9912 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=72ee1c45de759098
```
