# Confirm PASS — f173036c727472de on `filetypes/java_class`

Cycle `20260615T055200-confirm-f173036c727472de` — 2026-06-15T05:52:00Z

PR_AUC held across 3 seeds (orig 0.9883)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f173036c727472de` | `dafa4e0048daeebe` | `dafa4e0048daeebe` | `dafa4e0048daeebe` |
| PR AUC | 0.9883 | 0.9861 | 0.9868 | 0.9878 |
| ROC AUC | 0.9979 | 0.9974 | 0.9974 | 0.9978 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f173036c727472de
```
