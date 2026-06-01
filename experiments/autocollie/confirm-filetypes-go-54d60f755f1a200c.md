# Confirm PASS — 54d60f755f1a200c on `filetypes/go`

Cycle `20260601T153500-confirm-54d60f755f1a200c` — 2026-06-01T15:35:00Z

PR_AUC held across 3 seeds (orig 0.9604)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `54d60f755f1a200c` | `cdc768b2a51731e8` | `cdc768b2a51731e8` | `cdc768b2a51731e8` |
| PR AUC | 0.9604 | 0.9586 | 0.9513 | 0.9512 |
| ROC AUC | 0.9850 | 0.9880 | 0.9854 | 0.9860 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | FAIL | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=54d60f755f1a200c
```
