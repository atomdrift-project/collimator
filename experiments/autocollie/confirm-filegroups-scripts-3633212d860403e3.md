# Confirm PASS — 3633212d860403e3 on `filegroups/scripts`

Cycle `20260706T064522-confirm-3633212d860403e3` — 2026-07-06T06:45:22Z

PR_AUC held across 3 seeds (orig 0.9934)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3633212d860403e3` | `e48c4e9f0a55d58c` | `e48c4e9f0a55d58c` | `e48c4e9f0a55d58c` |
| PR AUC | 0.9934 | 0.9952 | 0.9953 | 0.9954 |
| ROC AUC | 0.9921 | 0.9961 | 0.9961 | 0.9962 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3633212d860403e3
```
