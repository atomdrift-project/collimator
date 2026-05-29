# Confirm PASS — 6967c6453db0f476 on `filetypes/html`

Cycle `20260527T055011-confirm-6967c6453db0f476` — 2026-05-27T05:50:11Z

PR_AUC held across 3 seeds (orig 0.0113)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6967c6453db0f476` | `8593ac3c5f66426f` | `8593ac3c5f66426f` | `8593ac3c5f66426f` |
| PR AUC | 0.0113 | 1.0000 | 1.0000 | 0.9861 |
| ROC AUC | 0.5000 | 1.0000 | 1.0000 | 0.9999 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 0.8750 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6967c6453db0f476
```
