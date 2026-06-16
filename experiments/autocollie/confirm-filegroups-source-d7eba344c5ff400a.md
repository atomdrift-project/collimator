# Confirm PASS — d7eba344c5ff400a on `filegroups/source`

Cycle `20260616T055047-confirm-d7eba344c5ff400a` — 2026-06-16T05:50:47Z

PR_AUC held across 3 seeds (orig 0.9975)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d7eba344c5ff400a` | `969f30982a596c8c` | `969f30982a596c8c` | `969f30982a596c8c` |
| PR AUC | 0.9975 | 0.9980 | 0.9980 | 0.9978 |
| ROC AUC | 0.9972 | 0.9977 | 0.9977 | 0.9975 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d7eba344c5ff400a
```
