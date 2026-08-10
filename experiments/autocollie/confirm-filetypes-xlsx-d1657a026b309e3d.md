# Confirm PASS — d1657a026b309e3d on `filetypes/xlsx`

Cycle `20260805T145528-confirm-d1657a026b309e3d` — 2026-08-05T14:55:28Z

PR_AUC held across 3 seeds (orig 0.9860)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d1657a026b309e3d` | `3d225a1f4b804e7c` | `3d225a1f4b804e7c` | `3d225a1f4b804e7c` |
| PR AUC | 0.9860 | 0.9881 | 0.9919 | 0.9854 |
| ROC AUC | 0.8197 | 0.7970 | 0.8681 | 0.7474 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d1657a026b309e3d
```
