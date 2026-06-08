# Confirm PASS — 72a917b3a48a6a2a on `filetypes/vbs`

Cycle `20260608T084404-confirm-72a917b3a48a6a2a` — 2026-06-08T08:44:04Z

PR_AUC held across 3 seeds (orig 0.9978)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `72a917b3a48a6a2a` | `91dbfac33b0c3480` | `91dbfac33b0c3480` | `91dbfac33b0c3480` |
| PR AUC | 0.9978 | 0.9979 | 0.9979 | 0.9979 |
| ROC AUC | 0.9926 | 0.9931 | 0.9928 | 0.9928 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=72a917b3a48a6a2a
```
