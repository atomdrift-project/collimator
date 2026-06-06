# Confirm PASS — 6646f71ad1a0a9f4 on `filetypes/zip`

Cycle `20260606T093147-confirm-6646f71ad1a0a9f4` — 2026-06-06T09:31:47Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6646f71ad1a0a9f4` | `2da2a85f3f3dec17` | `2da2a85f3f3dec17` | `2da2a85f3f3dec17` |
| PR AUC | 0.9998 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9980 | 0.9974 | 0.9974 | 0.9977 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6646f71ad1a0a9f4
```
