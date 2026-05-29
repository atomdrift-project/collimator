# Confirm PASS — 96078998a66fa551 on `filetypes/macho`

Cycle `20260526T225731-confirm-96078998a66fa551` — 2026-05-26T22:57:31Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `96078998a66fa551` | `759f968fd3fcee2d` | `759f968fd3fcee2d` | `759f968fd3fcee2d` |
| PR AUC | 0.9997 | 0.9974 | 0.9971 | 0.9966 |
| ROC AUC | 0.9999 | 0.9994 | 0.9993 | 0.9993 |
| Recall@3FPM | — | 0.9173 | 0.9286 | 0.7857 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=96078998a66fa551
```
