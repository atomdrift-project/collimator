# Confirm PASS — e3f2443bce3318a1 on `filetypes/pe`

Cycle `20260608T141044-confirm-e3f2443bce3318a1` — 2026-06-08T14:10:44Z

PR_AUC held across 3 seeds (orig 0.9984)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e3f2443bce3318a1` | `c704af735aa64eae` | `c704af735aa64eae` | `c704af735aa64eae` |
| PR AUC | 0.9984 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9986 | 0.9997 | 0.9996 | 0.9996 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e3f2443bce3318a1
```
