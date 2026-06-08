# Confirm PASS — 5aafc584acddea2e on `filetypes/python`

Cycle `20260608T182944-confirm-5aafc584acddea2e` — 2026-06-08T18:29:44Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5aafc584acddea2e` | `5ca4361c5cffb42b` | `5ca4361c5cffb42b` | `5ca4361c5cffb42b` |
| PR AUC | 0.9990 | 0.9944 | 0.9942 | 0.9942 |
| ROC AUC | 0.9990 | 0.9954 | 0.9953 | 0.9954 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5aafc584acddea2e
```
