# Confirm PASS — 743459da275d93a3 on `filetypes/deb`

Cycle `20260526T202237-confirm-743459da275d93a3` — 2026-05-26T20:22:37Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `743459da275d93a3` | `6ecde0436805a533` | `6ecde0436805a533` | `6ecde0436805a533` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=743459da275d93a3
```
