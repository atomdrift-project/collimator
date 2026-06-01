# Confirm PASS — 518a5a9843bcaf21 on `filetypes/pe`

Cycle `20260601T173435-confirm-518a5a9843bcaf21` — 2026-06-01T17:34:35Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `518a5a9843bcaf21` | `3ace146501d8132c` | `3ace146501d8132c` | `3ace146501d8132c` |
| PR AUC | 0.9994 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9995 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=518a5a9843bcaf21
```
