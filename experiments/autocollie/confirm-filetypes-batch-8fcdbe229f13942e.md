# Confirm PASS — 8fcdbe229f13942e on `filetypes/batch`

Cycle `20260615T061345-confirm-8fcdbe229f13942e` — 2026-06-15T06:13:45Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8fcdbe229f13942e` | `def5a9c5533fc5e9` | `def5a9c5533fc5e9` | `def5a9c5533fc5e9` |
| PR AUC | 0.9997 | 0.9997 | 0.9997 | 0.9997 |
| ROC AUC | 0.9982 | 0.9979 | 0.9978 | 0.9981 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8fcdbe229f13942e
```
