# Confirm PASS — c3024981770ef433 on `filetypes/elf`

Cycle `20260526T164216-confirm-c3024981770ef433` — 2026-05-26T16:42:16Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c3024981770ef433` | `7c1f59d99860a6c3` | `7c1f59d99860a6c3` | `7c1f59d99860a6c3` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 0.9754 | 0.9690 | 0.9778 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c3024981770ef433
```
