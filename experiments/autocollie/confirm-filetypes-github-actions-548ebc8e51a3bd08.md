# Confirm PASS — 548ebc8e51a3bd08 on `filetypes/github-actions`

Cycle `20260527T055339-confirm-548ebc8e51a3bd08` — 2026-05-27T05:53:39Z

PR_AUC held across 3 seeds (orig 0.0089)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `548ebc8e51a3bd08` | `7de1920413eeb70b` | `7de1920413eeb70b` | `7de1920413eeb70b` |
| PR AUC | 0.0089 | 0.0273 | 0.0273 | 0.0273 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=548ebc8e51a3bd08
```
