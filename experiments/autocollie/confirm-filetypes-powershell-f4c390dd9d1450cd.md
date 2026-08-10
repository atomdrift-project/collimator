# Confirm PASS — f4c390dd9d1450cd on `filetypes/powershell`

Cycle `20260804T211008-confirm-f4c390dd9d1450cd` — 2026-08-04T21:10:08Z

PR_AUC held across 3 seeds (orig 0.9936)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f4c390dd9d1450cd` | `96252e58859a8504` | `96252e58859a8504` | `96252e58859a8504` |
| PR AUC | 0.9936 | 0.9938 | 0.9940 | 0.9933 |
| ROC AUC | 0.9903 | 0.9907 | 0.9909 | 0.9894 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f4c390dd9d1450cd
```
