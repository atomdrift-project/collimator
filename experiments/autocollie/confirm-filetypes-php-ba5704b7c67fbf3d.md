# Confirm PASS — ba5704b7c67fbf3d on `filetypes/php`

Cycle `20260616T090007-confirm-ba5704b7c67fbf3d` — 2026-06-16T09:00:07Z

PR_AUC held across 3 seeds (orig 0.9953)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ba5704b7c67fbf3d` | `83cf14051cdcf8bb` | `83cf14051cdcf8bb` | `83cf14051cdcf8bb` |
| PR AUC | 0.9953 | 0.9953 | 0.9957 | 0.9962 |
| ROC AUC | 0.9978 | 0.9980 | 0.9979 | 0.9982 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ba5704b7c67fbf3d
```
