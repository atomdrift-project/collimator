# Confirm PASS — f9b6700f77bc10da on `filetypes/elf`

Cycle `20260613T022317-confirm-f9b6700f77bc10da` — 2026-06-13T02:23:17Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f9b6700f77bc10da` | `40a481de87a5f924` | `40a481de87a5f924` | `40a481de87a5f924` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9998 | 0.9999 | 1.0000 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f9b6700f77bc10da
```
