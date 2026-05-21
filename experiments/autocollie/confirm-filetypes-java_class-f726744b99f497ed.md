# Confirm PASS — f726744b99f497ed on `filetypes/java_class`

Cycle `20260521T044241-confirm-f726744b99f497ed` — 2026-05-21T04:42:41Z

PR_AUC held across 3 seeds (orig 0.9967)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f726744b99f497ed` | `0668b877a066d8a8` | `0668b877a066d8a8` | `0668b877a066d8a8` |
| PR AUC | 0.9967 | 0.9927 | 0.9958 | 0.9969 |
| ROC AUC | 0.9992 | 0.9984 | 0.9990 | 0.9992 |
| Recall@3FPM | — | 0.5400 | 0.7533 | 0.8733 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f726744b99f497ed
```
