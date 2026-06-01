# Confirm PASS — a8e61ee041d8f7f6 on `filetypes/macho`

Cycle `20260601T212157-confirm-a8e61ee041d8f7f6` — 2026-06-01T21:21:57Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a8e61ee041d8f7f6` | `3d93c3c9fd681de5` | `3d93c3c9fd681de5` | `3d93c3c9fd681de5` |
| PR AUC | 0.9996 | 0.9961 | 0.9961 | 0.9965 |
| ROC AUC | 0.9999 | 0.9990 | 0.9990 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a8e61ee041d8f7f6
```
