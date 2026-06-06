# Confirm PASS — 5ddd95a0558a7cee on `filetypes/vbs`

Cycle `20260606T073129-confirm-5ddd95a0558a7cee` — 2026-06-06T07:31:29Z

PR_AUC held across 3 seeds (orig 0.9975)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5ddd95a0558a7cee` | `be5e735eb73619e7` | `be5e735eb73619e7` | `be5e735eb73619e7` |
| PR AUC | 0.9975 | 0.9971 | 0.9979 | 0.9971 |
| ROC AUC | 0.9917 | 0.9902 | 0.9932 | 0.9902 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5ddd95a0558a7cee
```
