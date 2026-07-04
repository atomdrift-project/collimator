# Confirm PASS — 4defc3ac4afacdb9 on `filetypes/batch`

Cycle `20260704T135033-confirm-4defc3ac4afacdb9` — 2026-07-04T13:50:33Z

PR_AUC held across 3 seeds (orig 0.9895)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4defc3ac4afacdb9` | `f20d203d5a81883c` | `f20d203d5a81883c` | `f20d203d5a81883c` |
| PR AUC | 0.9895 | 0.9935 | 0.9928 | 0.9923 |
| ROC AUC | 0.9294 | 0.8955 | 0.8994 | 0.8880 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4defc3ac4afacdb9
```
