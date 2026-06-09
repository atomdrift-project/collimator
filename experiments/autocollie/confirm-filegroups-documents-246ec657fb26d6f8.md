# Confirm PASS — 246ec657fb26d6f8 on `filegroups/documents`

Cycle `20260609T111339-confirm-246ec657fb26d6f8` — 2026-06-09T11:13:39Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `246ec657fb26d6f8` | `e0b7facdc6e0e761` | `e0b7facdc6e0e761` | `e0b7facdc6e0e761` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9989 | 0.9991 | 0.9991 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=246ec657fb26d6f8
```
