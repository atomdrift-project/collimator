# Confirm PASS — a1841a05125432bb on `filetypes/perl`

Cycle `20260526T194619-confirm-a1841a05125432bb` — 2026-05-26T19:46:19Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a1841a05125432bb` | `cfae70c0175e470d` | `cfae70c0175e470d` | `cfae70c0175e470d` |
| PR AUC | 1.0000 | 0.9924 | 0.9959 | 0.9924 |
| ROC AUC | 1.0000 | 0.9992 | 0.9996 | 0.9992 |
| Recall@3FPM | — | 0.9524 | 0.9524 | 0.9524 |
| verdict | — | FAIL | PASS | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a1841a05125432bb
```
