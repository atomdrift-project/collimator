# Confirm PASS — 83e3a5e0bb842495 on `filetypes/deb`

Cycle `20260526T204750-confirm-83e3a5e0bb842495` — 2026-05-26T20:47:50Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `83e3a5e0bb842495` | `b5bdbf51e8721f2d` | `b5bdbf51e8721f2d` | `b5bdbf51e8721f2d` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=83e3a5e0bb842495
```
