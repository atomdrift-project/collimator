# Confirm PASS — cad3a137090e6b9f on `filetypes/shell`

Cycle `20260613T185642-confirm-cad3a137090e6b9f` — 2026-06-13T18:56:42Z

PR_AUC held across 3 seeds (orig 0.9960)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cad3a137090e6b9f` | `c58282b9918021af` | `c58282b9918021af` | `c58282b9918021af` |
| PR AUC | 0.9960 | 0.9970 | 0.9969 | 0.9971 |
| ROC AUC | 0.9974 | 0.9972 | 0.9971 | 0.9973 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cad3a137090e6b9f
```
