# Confirm PASS — 3373284695a7ab4e on `filetypes/deb`

Cycle `20260526T202809-confirm-3373284695a7ab4e` — 2026-05-26T20:28:09Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3373284695a7ab4e` | `81ee664f934d82f6` | `81ee664f934d82f6` | `81ee664f934d82f6` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3373284695a7ab4e
```
