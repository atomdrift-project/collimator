# Confirm PASS — bfef5f6b410e050a on `filegroups/documents`

Cycle `20260528T033426-confirm-bfef5f6b410e050a` — 2026-05-28T03:34:26Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bfef5f6b410e050a` | `3896f5c8f16f9508` | `3896f5c8f16f9508` | `3896f5c8f16f9508` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9997 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.9764 | 0.9819 | 0.9823 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bfef5f6b410e050a
```
