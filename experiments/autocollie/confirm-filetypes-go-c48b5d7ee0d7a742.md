# Confirm PASS — c48b5d7ee0d7a742 on `filetypes/go`

Cycle `20260628T135056-confirm-c48b5d7ee0d7a742` — 2026-06-28T13:50:56Z

PR_AUC held across 3 seeds (orig 0.9247)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c48b5d7ee0d7a742` | `87299b065570518e` | `87299b065570518e` | `87299b065570518e` |
| PR AUC | 0.9247 | 0.9191 | 0.9233 | 0.9212 |
| ROC AUC | 0.9763 | 0.9704 | 0.9722 | 0.9715 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c48b5d7ee0d7a742
```
