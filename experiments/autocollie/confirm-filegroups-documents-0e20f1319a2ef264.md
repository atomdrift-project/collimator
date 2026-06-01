# Confirm PASS — 0e20f1319a2ef264 on `filegroups/documents`

Cycle `20260601T143021-confirm-0e20f1319a2ef264` — 2026-06-01T14:30:21Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0e20f1319a2ef264` | `4c4d9705e236940b` | `4c4d9705e236940b` | `4c4d9705e236940b` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9998 | 0.9992 | 0.9992 | 0.9992 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0e20f1319a2ef264
```
