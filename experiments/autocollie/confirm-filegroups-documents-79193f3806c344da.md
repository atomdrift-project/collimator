# Confirm PASS — 79193f3806c344da on `filegroups/documents`

Cycle `20260606T145042-confirm-79193f3806c344da` — 2026-06-06T14:50:42Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `79193f3806c344da` | `2f679abc02b211c2` | `2f679abc02b211c2` | `2f679abc02b211c2` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9991 | 0.9991 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=79193f3806c344da
```
