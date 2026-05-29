# Confirm PASS — 3f8742c6d1f932de on `filetypes/docx`

Cycle `20260525T201410-confirm-3f8742c6d1f932de` — 2026-05-25T20:14:10Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3f8742c6d1f932de` | `32153ddbbb99a2c5` | `32153ddbbb99a2c5` | `32153ddbbb99a2c5` |
| PR AUC | 1.0000 | 0.9970 | 0.9975 | 0.9971 |
| ROC AUC | 1.0000 | 0.9830 | 0.9850 | 0.9835 |
| Recall@3FPM | — | 0.5133 | 0.5929 | 0.5177 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3f8742c6d1f932de
```
