# Confirm PASS — f6c00ae88555760a on `filetypes/kotlin`

Cycle `20260515T002700-confirm-f6c00ae88555760a` — 2026-05-15T00:27:00Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f6c00ae88555760a` | `2cf44129e4c6756d` | `2cf44129e4c6756d` | `2cf44129e4c6756d` |
| PR AUC | 1.0000 | 0.9996 | 1.0000 | 1.0000 |
| ROC AUC | 0.9994 | 0.9861 | 0.9986 | 0.9986 |
| Recall@3FPM | — | 0.9660 | 0.9794 | 0.9785 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f6c00ae88555760a
```
