# Confirm PASS — b8bb15cae84428aa on `filetypes/kotlin`

Cycle `20260710T191212-confirm-b8bb15cae84428aa` — 2026-07-10T19:12:12Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b8bb15cae84428aa` | `7cf575017c578491` | `7cf575017c578491` | `7cf575017c578491` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9992 | 0.9991 | 0.9991 | 0.9992 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b8bb15cae84428aa
```
