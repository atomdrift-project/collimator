# Confirm PASS — 95a9dc9199738046 on `filetypes/javascript`

Cycle `20260512T213149-confirm-95a9dc9199738046` — 2026-05-12T21:31:49Z

PR_AUC held across 3 seeds (orig 0.9998)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `95a9dc9199738046` | `dd617f28e464f8c3` | `dd617f28e464f8c3` | `dd617f28e464f8c3` |
| PR AUC | 0.9998 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9997 | 0.9997 | 0.9998 | 0.9997 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=95a9dc9199738046
```
