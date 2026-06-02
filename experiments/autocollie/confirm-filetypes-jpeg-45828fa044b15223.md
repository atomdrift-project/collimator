# Confirm PASS — 45828fa044b15223 on `filetypes/jpeg`

Cycle `20260602T024950-confirm-45828fa044b15223` — 2026-06-02T02:49:50Z

PR_AUC held across 3 seeds (orig 0.9407)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `45828fa044b15223` | `82b989fca3354578` | `82b989fca3354578` | `82b989fca3354578` |
| PR AUC | 0.9407 | 0.9491 | 0.9504 | 0.9687 |
| ROC AUC | 0.9691 | 0.9734 | 0.9746 | 0.9824 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=45828fa044b15223
```
