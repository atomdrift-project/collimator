# Confirm PASS — b568c66f05de7470 on `filetypes/java_class`

Cycle `20260616T053043-confirm-b568c66f05de7470` — 2026-06-16T05:30:43Z

PR_AUC held across 3 seeds (orig 0.9853)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b568c66f05de7470` | `4d4e7db58910877e` | `4d4e7db58910877e` | `4d4e7db58910877e` |
| PR AUC | 0.9853 | 0.9870 | 0.9873 | 0.9854 |
| ROC AUC | 0.9972 | 0.9976 | 0.9976 | 0.9971 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b568c66f05de7470
```
