# Confirm PASS — ef38980ac5a7919e on `filetypes/npm`

Cycle `20260804T235610-confirm-ef38980ac5a7919e` — 2026-08-04T23:56:10Z

PR_AUC held across 3 seeds (orig 0.9642)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ef38980ac5a7919e` | `0f2567fc35dae527` | `0f2567fc35dae527` | `0f2567fc35dae527` |
| PR AUC | 0.9642 | 0.9646 | 0.9643 | 0.9666 |
| ROC AUC | 0.9624 | 0.9626 | 0.9624 | 0.9646 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ef38980ac5a7919e
```
