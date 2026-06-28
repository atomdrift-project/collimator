# Confirm PASS — 12a6351c4610f24b on `filetypes/jar`

Cycle `20260628T014634-confirm-12a6351c4610f24b` — 2026-06-28T01:46:34Z

PR_AUC held across 3 seeds (orig 0.9832)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `12a6351c4610f24b` | `1466a314914264a0` | `1466a314914264a0` | `1466a314914264a0` |
| PR AUC | 0.9832 | 0.9862 | 0.9839 | 0.9836 |
| ROC AUC | 0.9712 | 0.9767 | 0.9727 | 0.9720 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=12a6351c4610f24b
```
