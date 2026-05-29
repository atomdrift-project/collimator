# Confirm PASS — 560011c5cf32fc2b on `filetypes/elf`

Cycle `20260528T105146-confirm-560011c5cf32fc2b` — 2026-05-28T10:51:46Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `560011c5cf32fc2b` | `fa02da7090dab84c` | `fa02da7090dab84c` | `fa02da7090dab84c` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 0.9645 | 0.9680 | 0.9563 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=560011c5cf32fc2b
```
