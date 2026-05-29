# Confirm PASS — 07bc5b056e10b50d on `filetypes/java_class`

Cycle `20260526T192527-confirm-07bc5b056e10b50d` — 2026-05-26T19:25:27Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `07bc5b056e10b50d` | `4fbd37f13e1fe5f4` | `4fbd37f13e1fe5f4` | `4fbd37f13e1fe5f4` |
| PR AUC | 1.0000 | 0.9961 | 0.9947 | 0.9939 |
| ROC AUC | 1.0000 | 0.9990 | 0.9987 | 0.9986 |
| Recall@3FPM | — | 0.8667 | 0.7333 | 0.6533 |
| verdict | — | PASS | FAIL | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=07bc5b056e10b50d
```
