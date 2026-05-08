# Confirm PASS — 158624a064a65fcb on `filetypes/php`

Cycle `20260508T200716-confirm-158624a064a65fcb` — 2026-05-08T20:07:16Z

F1 held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `158624a064a65fcb` | `acf757f53ad896f2` | `acf757f53ad896f2` | `acf757f53ad896f2` |
| F1 | 1.0000 | 1.0000 | 1.0000 | 0.9914 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| AP | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| recall@3 FP/M | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=158624a064a65fcb
```
