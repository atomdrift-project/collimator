# Confirm PASS — b5d4bb7f6a82d5bf on `filetypes/ole`

Cycle `20260608T021527-confirm-b5d4bb7f6a82d5bf` — 2026-06-08T02:15:27Z

PR_AUC held across 3 seeds (orig 0.9972)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b5d4bb7f6a82d5bf` | `dbbc2b459ac0e798` | `dbbc2b459ac0e798` | `dbbc2b459ac0e798` |
| PR AUC | 0.9972 | 0.9950 | 0.9969 | 0.9972 |
| ROC AUC | 0.9966 | 0.9938 | 0.9962 | 0.9965 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b5d4bb7f6a82d5bf
```
