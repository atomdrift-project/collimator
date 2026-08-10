# Confirm PASS — 7a70f0c368c9a0ea on `filetypes/batch`

Cycle `20260805T145600-confirm-7a70f0c368c9a0ea` — 2026-08-05T14:56:00Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `7a70f0c368c9a0ea` | `da5fa11b26015642` | `da5fa11b26015642` | `da5fa11b26015642` |
| PR AUC | 0.9990 | 0.9985 | 0.9980 | 0.9996 |
| ROC AUC | 0.9928 | 0.9778 | 0.9659 | 0.9933 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=7a70f0c368c9a0ea
```
