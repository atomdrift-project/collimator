# Confirm PASS — 7a6595cd3fe217ad on `filetypes/java`

Cycle `20260606T180855-confirm-7a6595cd3fe217ad` — 2026-06-06T18:08:55Z

PR_AUC held across 3 seeds (orig 0.5159)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7a6595cd3fe217ad` | `a4a429ee2a8ab16f` | `a4a429ee2a8ab16f` | `a4a429ee2a8ab16f` |
| PR AUC | 0.5159 | 0.9007 | 0.8915 | 0.9161 |
| ROC AUC | 0.8438 | 0.9182 | 0.9409 | 0.9455 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7a6595cd3fe217ad
```
