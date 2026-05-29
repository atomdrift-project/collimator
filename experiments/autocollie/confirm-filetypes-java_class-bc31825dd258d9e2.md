# Confirm PASS — bc31825dd258d9e2 on `filetypes/java_class`

Cycle `20260526T193508-confirm-bc31825dd258d9e2` — 2026-05-26T19:35:08Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bc31825dd258d9e2` | `a541713995dc5e9b` | `a541713995dc5e9b` | `a541713995dc5e9b` |
| PR AUC | 1.0000 | 0.9954 | 0.9947 | 0.9961 |
| ROC AUC | 1.0000 | 0.9989 | 0.9987 | 0.9990 |
| Recall@3FPM | — | 0.8267 | 0.7400 | 0.8533 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bc31825dd258d9e2
```
