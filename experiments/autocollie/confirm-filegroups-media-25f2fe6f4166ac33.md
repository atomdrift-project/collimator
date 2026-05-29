# Confirm PASS — 25f2fe6f4166ac33 on `filegroups/media`

Cycle `20260526T235516-confirm-25f2fe6f4166ac33` — 2026-05-26T23:55:16Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `25f2fe6f4166ac33` | `a01b31cf83c18f72` | `a01b31cf83c18f72` | `a01b31cf83c18f72` |
| PR AUC | 0.9990 | 0.9973 | 0.9982 | 0.9989 |
| ROC AUC | 0.9988 | 0.9968 | 0.9980 | 0.9987 |
| Recall@3FPM | — | 0.9111 | 0.9000 | 0.9667 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=25f2fe6f4166ac33
```
