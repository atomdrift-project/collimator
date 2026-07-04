# Confirm PASS — 0afbf409ae8998d1 on `filetypes/elf`

Cycle `20260704T125556-confirm-0afbf409ae8998d1` — 2026-07-04T12:55:56Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0afbf409ae8998d1` | `5e1c9cbcdefd84d2` | `5e1c9cbcdefd84d2` | `5e1c9cbcdefd84d2` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0afbf409ae8998d1
```
