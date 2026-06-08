# Confirm PASS — 07066c4d765de183 on `filetypes/php`

Cycle `20260608T113405-confirm-07066c4d765de183` — 2026-06-08T11:34:05Z

PR_AUC held across 3 seeds (orig 0.9942)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `07066c4d765de183` | `6f902d0d6793a9c0` | `6f902d0d6793a9c0` | `6f902d0d6793a9c0` |
| PR AUC | 0.9942 | 0.9938 | 0.9943 | 0.9939 |
| ROC AUC | 0.9969 | 0.9968 | 0.9968 | 0.9967 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=07066c4d765de183
```
