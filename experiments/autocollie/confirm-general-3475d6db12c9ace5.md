# Confirm PASS — 3475d6db12c9ace5 on `general`

Cycle `20260524T091339-confirm-3475d6db12c9ace5` — 2026-05-24T09:13:39Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3475d6db12c9ace5` | `cee48539a4b932be` | `cee48539a4b932be` | `cee48539a4b932be` |
| PR AUC | 0.9988 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9988 | 0.9997 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.7037 | 0.6532 | 0.6621 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3475d6db12c9ace5
```
