# Confirm PASS — e789cb47deff697c on `filetypes/lnk`

Cycle `20260527T000201-confirm-e789cb47deff697c` — 2026-05-27T00:02:01Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e789cb47deff697c` | `8bd61d09d25e9acf` | `8bd61d09d25e9acf` | `8bd61d09d25e9acf` |
| PR AUC | 0.9990 | 0.9987 | 0.9990 | 0.9989 |
| ROC AUC | 0.9869 | 0.9826 | 0.9870 | 0.9860 |
| Recall@3FPM | — | 0.9128 | 0.9590 | 0.9487 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e789cb47deff697c
```
