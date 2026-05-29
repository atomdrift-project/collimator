# Confirm PASS — 271acc64b3a7fd1a on `filetypes/perl`

Cycle `20260525T195046-confirm-271acc64b3a7fd1a` — 2026-05-25T19:50:46Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `271acc64b3a7fd1a` | `e16b518d59c52227` | `e16b518d59c52227` | `e16b518d59c52227` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 0.9956 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 0.9996 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 0.9048 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=271acc64b3a7fd1a
```
