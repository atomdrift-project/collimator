# Confirm PASS — d1e556d86f7fdd95 on `filetypes/php`

Cycle `20260603T155528-confirm-d1e556d86f7fdd95` — 2026-06-03T15:55:28Z

PR_AUC held across 3 seeds (orig 0.9958)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d1e556d86f7fdd95` | `36609aed60ec547a` | `36609aed60ec547a` | `36609aed60ec547a` |
| PR AUC | 0.9958 | 0.9959 | 0.9959 | 0.9955 |
| ROC AUC | 0.9976 | 0.9976 | 0.9978 | 0.9974 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d1e556d86f7fdd95
```
