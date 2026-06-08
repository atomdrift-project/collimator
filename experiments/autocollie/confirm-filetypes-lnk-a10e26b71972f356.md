# Confirm PASS — a10e26b71972f356 on `filetypes/lnk`

Cycle `20260608T070049-confirm-a10e26b71972f356` — 2026-06-08T07:00:49Z

PR_AUC held across 3 seeds (orig 0.9957)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a10e26b71972f356` | `7e78bd016dc2d5a5` | `7e78bd016dc2d5a5` | `7e78bd016dc2d5a5` |
| PR AUC | 0.9957 | 0.9961 | 0.9965 | 0.9955 |
| ROC AUC | 0.9808 | 0.9828 | 0.9846 | 0.9802 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a10e26b71972f356
```
