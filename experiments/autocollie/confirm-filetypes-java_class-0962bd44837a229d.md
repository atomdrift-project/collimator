# Confirm PASS — 0962bd44837a229d on `filetypes/java_class`

Cycle `20260608T003613-confirm-0962bd44837a229d` — 2026-06-08T00:36:13Z

PR_AUC held across 3 seeds (orig 0.9895)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0962bd44837a229d` | `8c2d488c918c302d` | `8c2d488c918c302d` | `8c2d488c918c302d` |
| PR AUC | 0.9895 | 0.9907 | 0.9892 | 0.9899 |
| ROC AUC | 0.9976 | 0.9980 | 0.9979 | 0.9981 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0962bd44837a229d
```
