# Confirm PASS — b0756a90274b0c7a on `filegroups/config`

Cycle `20260526T154142-confirm-b0756a90274b0c7a` — 2026-05-26T15:41:42Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b0756a90274b0c7a` | `5f1f831f446f53df` | `5f1f831f446f53df` | `5f1f831f446f53df` |
| PR AUC | 0.9998 | 0.9998 | 0.9998 | 0.9999 |
| ROC AUC | 0.9995 | 0.9997 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.8739 | 0.8683 | 0.9513 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b0756a90274b0c7a
```
