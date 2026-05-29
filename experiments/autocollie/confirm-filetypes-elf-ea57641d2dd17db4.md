# Confirm PASS — ea57641d2dd17db4 on `filetypes/elf`

Cycle `20260525T192455-confirm-ea57641d2dd17db4` — 2026-05-25T19:24:55Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ea57641d2dd17db4` | `110d6ac07d5c7d89` | `110d6ac07d5c7d89` | `110d6ac07d5c7d89` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 0.9774 | 0.9809 | 0.9788 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ea57641d2dd17db4
```
