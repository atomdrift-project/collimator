# Confirm PASS — f631902369e1a0bd on `filetypes/java_class`

Cycle `20260628T081951-confirm-f631902369e1a0bd` — 2026-06-28T08:19:51Z

PR_AUC held across 3 seeds (orig 0.9794)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f631902369e1a0bd` | `3d91188c3b42f2f1` | `3d91188c3b42f2f1` | `3d91188c3b42f2f1` |
| PR AUC | 0.9794 | 0.9773 | 0.9759 | 0.9786 |
| ROC AUC | 0.9962 | 0.9965 | 0.9963 | 0.9968 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f631902369e1a0bd
```
