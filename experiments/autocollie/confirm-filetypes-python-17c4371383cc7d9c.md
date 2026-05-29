# Confirm PASS — 17c4371383cc7d9c on `filetypes/python`

Cycle `20260527T001005-confirm-17c4371383cc7d9c` — 2026-05-27T00:10:05Z

PR_AUC held across 3 seeds (orig 0.9992)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `17c4371383cc7d9c` | `d0f9b2242c9b68ce` | `d0f9b2242c9b68ce` | `d0f9b2242c9b68ce` |
| PR AUC | 0.9992 | 0.9986 | 0.9982 | 0.9986 |
| ROC AUC | 0.9992 | 0.9988 | 0.9985 | 0.9987 |
| Recall@3FPM | — | 0.8313 | 0.7181 | 0.8350 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=17c4371383cc7d9c
```
