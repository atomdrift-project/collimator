# Confirm PASS — 68d6e54d9c7b48c2 on `general`

Cycle `20260608T112929-confirm-68d6e54d9c7b48c2` — 2026-06-08T11:29:29Z

PR_AUC held across 3 seeds (orig 0.9981)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `68d6e54d9c7b48c2` | `f1f65b09593fd9f7` | `f1f65b09593fd9f7` | `f1f65b09593fd9f7` |
| PR AUC | 0.9981 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9980 | 0.9994 | 0.9994 | 0.9994 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=68d6e54d9c7b48c2
```
