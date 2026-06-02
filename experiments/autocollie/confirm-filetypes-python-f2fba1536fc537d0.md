# Confirm PASS — f2fba1536fc537d0 on `filetypes/python`

Cycle `20260602T010511-confirm-f2fba1536fc537d0` — 2026-06-02T01:05:11Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f2fba1536fc537d0` | `b4269d5b16803e77` | `b4269d5b16803e77` | `b4269d5b16803e77` |
| PR AUC | 0.9989 | 0.9973 | 0.9973 | 0.9972 |
| ROC AUC | 0.9989 | 0.9980 | 0.9980 | 0.9979 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f2fba1536fc537d0
```
