# Confirm PASS — bae09c4f075b41fe on `filetypes/deb`

Cycle `20260526T204117-confirm-bae09c4f075b41fe` — 2026-05-26T20:41:17Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bae09c4f075b41fe` | `8df821ac40a677c6` | `8df821ac40a677c6` | `8df821ac40a677c6` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bae09c4f075b41fe
```
