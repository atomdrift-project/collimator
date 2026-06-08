# Confirm PASS — 58aa1da5c3daf5f0 on `filetypes/python`

Cycle `20260608T182859-confirm-58aa1da5c3daf5f0` — 2026-06-08T18:28:59Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `58aa1da5c3daf5f0` | `dbb82e87fad027c8` | `dbb82e87fad027c8` | `dbb82e87fad027c8` |
| PR AUC | 0.9990 | 0.9940 | 0.9944 | 0.9941 |
| ROC AUC | 0.9990 | 0.9951 | 0.9954 | 0.9952 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=58aa1da5c3daf5f0
```
