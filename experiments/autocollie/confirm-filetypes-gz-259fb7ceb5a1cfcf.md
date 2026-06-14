# Confirm PASS — 259fb7ceb5a1cfcf on `filetypes/gz`

Cycle `20260614T031548-confirm-259fb7ceb5a1cfcf` — 2026-06-14T03:15:48Z

PR_AUC held across 3 seeds (orig 0.7112)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `259fb7ceb5a1cfcf` | `4890fd56d9208ea1` | `4890fd56d9208ea1` | `4890fd56d9208ea1` |
| PR AUC | 0.7112 | 0.7298 | 0.7272 | 0.7279 |
| ROC AUC | 0.8879 | 0.8970 | 0.8980 | 0.8867 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=259fb7ceb5a1cfcf
```
