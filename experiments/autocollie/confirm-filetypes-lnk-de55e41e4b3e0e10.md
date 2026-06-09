# Confirm PASS — de55e41e4b3e0e10 on `filetypes/lnk`

Cycle `20260609T080353-confirm-de55e41e4b3e0e10` — 2026-06-09T08:03:53Z

PR_AUC held across 3 seeds (orig 0.9955)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `de55e41e4b3e0e10` | `6befa219d32df4d4` | `6befa219d32df4d4` | `6befa219d32df4d4` |
| PR AUC | 0.9955 | 0.9958 | 0.9963 | 0.9956 |
| ROC AUC | 0.9798 | 0.9815 | 0.9834 | 0.9802 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=de55e41e4b3e0e10
```
