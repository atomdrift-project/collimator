# Confirm PASS — a73081138e09f95b on `filetypes/perl`

Cycle `20260520T053837-confirm-a73081138e09f95b` — 2026-05-20T05:38:37Z

PR_AUC held across 3 seeds (orig 0.9959)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a73081138e09f95b` | `a2ee9ffbf67814b9` | `a2ee9ffbf67814b9` | `a2ee9ffbf67814b9` |
| PR AUC | 0.9959 | 0.9978 | 0.9908 | 0.9959 |
| ROC AUC | 0.9996 | 0.9998 | 0.9989 | 0.9996 |
| Recall@3FPM | — | 0.9524 | 0.9524 | 0.9524 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a73081138e09f95b
```
