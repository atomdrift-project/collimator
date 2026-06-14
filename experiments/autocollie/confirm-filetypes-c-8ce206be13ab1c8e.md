# Confirm PASS — 8ce206be13ab1c8e on `filetypes/c`

Cycle `20260614T210544-confirm-8ce206be13ab1c8e` — 2026-06-14T21:05:44Z

PR_AUC held across 3 seeds (orig 0.9830)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8ce206be13ab1c8e` | `bde7e6275c406640` | `bde7e6275c406640` | `bde7e6275c406640` |
| PR AUC | 0.9830 | 0.9840 | 0.9836 | 0.9835 |
| ROC AUC | 0.9927 | 0.9927 | 0.9927 | 0.9929 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8ce206be13ab1c8e
```
