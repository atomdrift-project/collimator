# Confirm PASS — 2d775b0afbffe348 on `filegroups/documents`

Cycle `20260705T172520-confirm-2d775b0afbffe348` — 2026-07-05T17:25:20Z

PR_AUC held across 3 seeds (orig 0.9332)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2d775b0afbffe348` | `f0d45e92fae32fb2` | `f0d45e92fae32fb2` | `f0d45e92fae32fb2` |
| PR AUC | 0.9332 | 0.9795 | 0.9789 | 0.9785 |
| ROC AUC | 0.9052 | 0.9065 | 0.9017 | 0.9026 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2d775b0afbffe348
```
