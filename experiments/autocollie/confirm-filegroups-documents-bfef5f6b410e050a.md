# Confirm PASS — bfef5f6b410e050a on `filegroups/documents`

Cycle `20260601T131839-confirm-bfef5f6b410e050a` — 2026-06-01T13:18:39Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bfef5f6b410e050a` | `f170bdf0f26bf264` | `f170bdf0f26bf264` | `f170bdf0f26bf264` |
| PR AUC | 1.0000 | 0.9999 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9972 | 0.9992 | 0.9992 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bfef5f6b410e050a
```
