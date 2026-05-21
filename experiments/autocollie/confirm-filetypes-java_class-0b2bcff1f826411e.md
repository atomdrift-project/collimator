# Confirm PASS — 0b2bcff1f826411e on `filetypes/java_class`

Cycle `20260521T072744-confirm-0b2bcff1f826411e` — 2026-05-21T07:27:44Z

PR_AUC held across 3 seeds (orig 0.9967)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0b2bcff1f826411e` | `5a48045d5eee70b7` | `5a48045d5eee70b7` | `5a48045d5eee70b7` |
| PR AUC | 0.9967 | 0.9927 | 0.9958 | 0.9969 |
| ROC AUC | 0.9992 | 0.9984 | 0.9990 | 0.9992 |
| Recall@3FPM | — | 0.5400 | 0.7533 | 0.8733 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0b2bcff1f826411e
```
