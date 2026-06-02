# Confirm PASS — 0b15b29be45cc13a on `filetypes/c`

Cycle `20260602T004650-confirm-0b15b29be45cc13a` — 2026-06-02T00:46:50Z

PR_AUC held across 3 seeds (orig 0.9904)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0b15b29be45cc13a` | `04e623d50363ed4a` | `04e623d50363ed4a` | `04e623d50363ed4a` |
| PR AUC | 0.9904 | 0.9886 | 0.9895 | 0.9888 |
| ROC AUC | 0.9951 | 0.9947 | 0.9951 | 0.9946 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0b15b29be45cc13a
```
