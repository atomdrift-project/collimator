# Confirm PASS — a9c235d19e755d39 on `filetypes/elf`

Cycle `20260703T005740-confirm-a9c235d19e755d39` — 2026-07-03T00:57:40Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a9c235d19e755d39` | `1619c7475fd88119` | `1619c7475fd88119` | `1619c7475fd88119` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9998 | 0.9999 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a9c235d19e755d39
```
