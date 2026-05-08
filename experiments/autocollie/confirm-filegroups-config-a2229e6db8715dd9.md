# Confirm PASS — a2229e6db8715dd9 on `filegroups/config`

Cycle `20260508T150127-confirm-a2229e6db8715dd9` — 2026-05-08T15:01:27Z

F1 held across 3 seeds (orig 0.9971)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a2229e6db8715dd9` | `3a5594a92a207e20` | `3a5594a92a207e20` | `3a5594a92a207e20` |
| F1 | 0.9971 | 0.9968 | 0.9968 | 0.9965 |
| ROC AUC | 0.9996 | 0.9996 | 0.9996 | 0.9995 |
| AP | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| recall@3 FP/M | 0.9065 | 0.8358 | 0.8358 | 0.8358 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a2229e6db8715dd9
```
