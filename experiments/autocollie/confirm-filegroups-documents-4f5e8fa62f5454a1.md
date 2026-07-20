# Confirm PASS — 4f5e8fa62f5454a1 on `filegroups/documents`

Cycle `20260713T032441-confirm-4f5e8fa62f5454a1` — 2026-07-13T03:24:41Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4f5e8fa62f5454a1` | `e30129a25bb26d5b` | `e30129a25bb26d5b` | `e30129a25bb26d5b` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9989 | 0.9991 | 0.9992 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4f5e8fa62f5454a1
```
