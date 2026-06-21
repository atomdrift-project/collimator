# Confirm PASS — c09cff946dc8778b on `filetypes/rust`

Cycle `20260617T182001-confirm-c09cff946dc8778b` — 2026-06-17T18:20:01Z

PR_AUC held across 3 seeds (orig 0.9073)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c09cff946dc8778b` | `3702d061e44644e4` | `3702d061e44644e4` | `3702d061e44644e4` |
| PR AUC | 0.9073 | 0.9406 | 0.8520 | 0.9113 |
| ROC AUC | 0.9908 | 0.9952 | 0.9888 | 0.9934 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c09cff946dc8778b
```
