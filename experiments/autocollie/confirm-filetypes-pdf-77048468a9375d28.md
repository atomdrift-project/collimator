# Confirm PASS — 77048468a9375d28 on `filetypes/pdf`

Cycle `20260710T183335-confirm-77048468a9375d28` — 2026-07-10T18:33:35Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `77048468a9375d28` | `1653acd1cec85c7b` | `1653acd1cec85c7b` | `1653acd1cec85c7b` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9995 | 0.9992 | 0.9986 | 0.9986 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=77048468a9375d28
```
