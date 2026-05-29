# Confirm PASS — 9312264d7b39f88e on `filetypes/pptx`

Cycle `20260525T214759-confirm-9312264d7b39f88e` — 2026-05-25T21:47:59Z

PR_AUC held across 3 seeds (orig 0.9231)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9312264d7b39f88e` | `21dcd81b59969a41` | `21dcd81b59969a41` | `21dcd81b59969a41` |
| PR AUC | 0.9231 | 0.9231 | 0.9231 | 0.9231 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9312264d7b39f88e
```
