# Confirm PASS — 02bd73a11c92a3d7 on `filetypes/java_class`

Cycle `20260508T202927-confirm-02bd73a11c92a3d7` — 2026-05-08T20:29:27Z

F1 held across 3 seeds (orig 0.9922)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `02bd73a11c92a3d7` | `2a519bbf2266f883` | `2a519bbf2266f883` | `2a519bbf2266f883` |
| F1 | 0.9922 | 1.0000 | 0.9844 | 0.9924 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| AP | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| recall@3 FP/M | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=02bd73a11c92a3d7
```
