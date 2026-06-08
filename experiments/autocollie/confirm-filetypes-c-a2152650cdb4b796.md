# Confirm PASS — a2152650cdb4b796 on `filetypes/c`

Cycle `20260608T115047-confirm-a2152650cdb4b796` — 2026-06-08T11:50:47Z

PR_AUC held across 3 seeds (orig 0.9862)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a2152650cdb4b796` | `d128bb35b9b77f3c` | `d128bb35b9b77f3c` | `d128bb35b9b77f3c` |
| PR AUC | 0.9862 | 0.9862 | 0.9861 | 0.9865 |
| ROC AUC | 0.9939 | 0.9937 | 0.9938 | 0.9937 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a2152650cdb4b796
```
