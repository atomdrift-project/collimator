# Confirm PASS — d86b22aa9130ad30 on `filetypes/text`

Cycle `20260617T174629-confirm-d86b22aa9130ad30` — 2026-06-17T17:46:29Z

PR_AUC held across 3 seeds (orig 0.9414)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d86b22aa9130ad30` | `1de03061afc23afc` | `1de03061afc23afc` | `1de03061afc23afc` |
| PR AUC | 0.9414 | 0.9323 | 0.9318 | 0.9358 |
| ROC AUC | 0.9695 | 0.9658 | 0.9633 | 0.9643 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d86b22aa9130ad30
```
