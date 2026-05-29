# Confirm PASS — 8e9299d4cc7de4a3 on `filetypes/gz`

Cycle `20260526T205313-confirm-8e9299d4cc7de4a3` — 2026-05-26T20:53:13Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8e9299d4cc7de4a3` | `c6f07eff70a29223` | `c6f07eff70a29223` | `c6f07eff70a29223` |
| PR AUC | 1.0000 | 0.9981 | 0.9986 | 0.9987 |
| ROC AUC | 1.0000 | 0.9973 | 0.9982 | 0.9982 |
| Recall@3FPM | — | 0.9913 | 0.9913 | 0.9913 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8e9299d4cc7de4a3
```
