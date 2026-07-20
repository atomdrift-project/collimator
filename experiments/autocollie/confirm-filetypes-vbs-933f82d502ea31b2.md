# Confirm PASS — 933f82d502ea31b2 on `filetypes/vbs`

Cycle `20260711T131803-confirm-933f82d502ea31b2` — 2026-07-11T13:18:03Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `933f82d502ea31b2` | `10e461361332f068` | `10e461361332f068` | `10e461361332f068` |
| PR AUC | 0.9998 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9973 | 0.9969 | 0.9971 | 0.9962 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=933f82d502ea31b2
```
