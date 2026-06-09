# Confirm PASS — 48a5aa5cbdd77c90 on `filetypes/ole`

Cycle `20260609T080849-confirm-48a5aa5cbdd77c90` — 2026-06-09T08:08:49Z

PR_AUC held across 3 seeds (orig 0.9947)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `48a5aa5cbdd77c90` | `8d1344dcd23b114f` | `8d1344dcd23b114f` | `8d1344dcd23b114f` |
| PR AUC | 0.9947 | 0.9941 | 0.9946 | 0.9941 |
| ROC AUC | 0.9936 | 0.9929 | 0.9934 | 0.9929 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=48a5aa5cbdd77c90
```
