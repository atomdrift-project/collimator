# Confirm PASS — c8c3fced3218855b on `filetypes/java`

Cycle `20260609T100112-confirm-c8c3fced3218855b` — 2026-06-09T10:01:12Z

PR_AUC held across 3 seeds (orig 0.9705)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c8c3fced3218855b` | `d7d6e20555c39011` | `d7d6e20555c39011` | `d7d6e20555c39011` |
| PR AUC | 0.9705 | 0.9773 | 0.9757 | 0.9710 |
| ROC AUC | 0.9650 | 0.9683 | 0.9661 | 0.9650 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c8c3fced3218855b
```
