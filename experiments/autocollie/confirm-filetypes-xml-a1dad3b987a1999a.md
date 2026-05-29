# Confirm PASS — a1dad3b987a1999a on `filetypes/xml`

Cycle `20260526T201010-confirm-a1dad3b987a1999a` — 2026-05-26T20:10:10Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a1dad3b987a1999a` | `6fdece4868464f39` | `6fdece4868464f39` | `6fdece4868464f39` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a1dad3b987a1999a
```
