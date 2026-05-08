# Confirm PASS — eccbedd1ed54fc8a on `filetypes/pe`

Cycle `20260508T034543-confirm-eccbedd1ed54fc8a` — 2026-05-08T03:45:43Z

F1 held across 3 seeds (orig 0.9974)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `eccbedd1ed54fc8a` | `d3bef1d7e564670b` | `72dab83846029f24` | `73a8ffbff887e5a6` |
| F1 | 0.9974 | 0.9966 | 0.9969 | 0.9972 |
| ROC AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| AP | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| recall@3 FP/M | 0.6591 | 0.6012 | 0.7540 | 0.7591 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=eccbedd1ed54fc8a
```
