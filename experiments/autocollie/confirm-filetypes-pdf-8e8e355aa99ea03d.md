# Confirm PASS — 8e8e355aa99ea03d on `filetypes/pdf`

Cycle `20260827T100300-confirm-8e8e355aa99ea03d` — 2026-08-27T10:03:00Z

PR_AUC held across 3 seeds (orig 0.9980)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8e8e355aa99ea03d` | `ca0e3e40c3898dbb` | `ca0e3e40c3898dbb` | `ca0e3e40c3898dbb` |
| PR AUC | 0.9980 | 0.9991 | 0.9992 | 0.9981 |
| ROC AUC | 0.9934 | 0.9944 | 0.9950 | 0.9884 |
| Recall@L50 | — | 0.7693 | 0.8362 | 0.7601 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8e8e355aa99ea03d
```
