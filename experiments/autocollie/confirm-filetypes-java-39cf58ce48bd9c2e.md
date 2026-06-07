# Confirm PASS — 39cf58ce48bd9c2e on `filetypes/java`

Cycle `20260606T180857-confirm-39cf58ce48bd9c2e` — 2026-06-06T18:08:57Z

PR_AUC held across 3 seeds (orig 0.6056)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `39cf58ce48bd9c2e` | `58ad7a5685267dbb` | `58ad7a5685267dbb` | `58ad7a5685267dbb` |
| PR AUC | 0.6056 | 0.9217 | 0.9443 | 0.9233 |
| ROC AUC | 0.8125 | 0.9386 | 0.9705 | 0.9636 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=39cf58ce48bd9c2e
```
