# Confirm PASS — 31323f3534358eee on `filetypes/csharp`

Cycle `20260608T120318-confirm-31323f3534358eee` — 2026-06-08T12:03:18Z

PR_AUC held across 3 seeds (orig 0.9903)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `31323f3534358eee` | `d4d3131a89872a1e` | `d4d3131a89872a1e` | `d4d3131a89872a1e` |
| PR AUC | 0.9903 | 0.9896 | 0.9878 | 0.9886 |
| ROC AUC | 0.9933 | 0.9937 | 0.9921 | 0.9913 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=31323f3534358eee
```
