# Confirm PASS — becf26ff52bff163 on `filetypes/zip`

Cycle `20260528T120859-confirm-becf26ff52bff163` — 2026-05-28T12:08:59Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `becf26ff52bff163` | `3b2acb4890542414` | `3b2acb4890542414` | `3b2acb4890542414` |
| PR AUC | 0.9997 | 0.9997 | 0.9997 | 0.9997 |
| ROC AUC | 0.9957 | 0.9959 | 0.9959 | 0.9957 |
| Recall@3FPM | — | 0.6831 | 0.6892 | 0.6963 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=becf26ff52bff163
```
