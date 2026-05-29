# Confirm PASS — 52ecadaa576a0d96 on `filetypes/xml`

Cycle `20260526T194635-confirm-52ecadaa576a0d96` — 2026-05-26T19:46:35Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `52ecadaa576a0d96` | `a4c0161792f64dd1` | `a4c0161792f64dd1` | `a4c0161792f64dd1` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 0.9989 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 0.9998 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 0.9655 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=52ecadaa576a0d96
```
