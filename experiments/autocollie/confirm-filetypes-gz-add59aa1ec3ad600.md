# Confirm PASS — add59aa1ec3ad600 on `filetypes/gz`

Cycle `20260613T193733-confirm-add59aa1ec3ad600` — 2026-06-13T19:37:33Z

PR_AUC held across 3 seeds (orig 0.7184)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `add59aa1ec3ad600` | `c976a1f9509b56cc` | `c976a1f9509b56cc` | `c976a1f9509b56cc` |
| PR AUC | 0.7184 | 0.7287 | 0.7302 | 0.7144 |
| ROC AUC | 0.8380 | 0.8995 | 0.8990 | 0.8886 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=add59aa1ec3ad600
```
