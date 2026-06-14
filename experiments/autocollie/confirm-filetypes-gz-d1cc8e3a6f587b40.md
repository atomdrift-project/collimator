# Confirm PASS — d1cc8e3a6f587b40 on `filetypes/gz`

Cycle `20260614T032245-confirm-d1cc8e3a6f587b40` — 2026-06-14T03:22:45Z

PR_AUC held across 3 seeds (orig 0.7117)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d1cc8e3a6f587b40` | `ac2c0ec77c8bc740` | `ac2c0ec77c8bc740` | `ac2c0ec77c8bc740` |
| PR AUC | 0.7117 | 0.7250 | 0.7167 | 0.7302 |
| ROC AUC | 0.8765 | 0.8474 | 0.8892 | 0.8904 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d1cc8e3a6f587b40
```
