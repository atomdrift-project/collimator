# Confirm PASS — cd6fdd63d14dfec5 on `filetypes/ole`

Cycle `20260508T094615-confirm-cd6fdd63d14dfec5` — 2026-05-08T09:46:15Z

F1 held across 3 seeds (orig 0.9565)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cd6fdd63d14dfec5` | `36aed436435a0da3` | `0e74d3d21e0dbd98` | `b517a7a38ef0f78d` |
| F1 | 0.9565 | 1.0000 | 0.9778 | 0.9767 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| AP | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| recall@3 FP/M | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cd6fdd63d14dfec5
```
