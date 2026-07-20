# Confirm PASS — a40ab80d95ae28bf on `filetypes/kotlin`

Cycle `20260718T154032-confirm-a40ab80d95ae28bf` — 2026-07-18T15:40:32Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a40ab80d95ae28bf` | `6a52eb4d54ea5657` | `6a52eb4d54ea5657` | `6a52eb4d54ea5657` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 | 0.9999 |
| ROC AUC | 0.9949 | 0.9990 | 0.9989 | 0.9974 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a40ab80d95ae28bf
```
