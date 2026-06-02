# Confirm PASS — a60148eff39255c8 on `filetypes/c`

Cycle `20260602T003442-confirm-a60148eff39255c8` — 2026-06-02T00:34:42Z

PR_AUC held across 3 seeds (orig 0.9918)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a60148eff39255c8` | `5f14e60203dbeee2` | `5f14e60203dbeee2` | `5f14e60203dbeee2` |
| PR AUC | 0.9918 | 0.9891 | 0.9894 | 0.9888 |
| ROC AUC | 0.9957 | 0.9949 | 0.9951 | 0.9945 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a60148eff39255c8
```
