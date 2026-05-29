# Confirm PASS — f73dd43ec8d24d91 on `filetypes/groovy`

Cycle `20260527T075328-confirm-f73dd43ec8d24d91` — 2026-05-27T07:53:28Z

PR_AUC held across 3 seeds (orig 0.6667)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f73dd43ec8d24d91` | `357a09ef67b0bf09` | `357a09ef67b0bf09` | `357a09ef67b0bf09` |
| PR AUC | 0.6667 | 0.6667 | 0.6667 | 0.6667 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f73dd43ec8d24d91
```
