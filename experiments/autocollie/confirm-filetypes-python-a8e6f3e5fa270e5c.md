# Confirm PASS — a8e6f3e5fa270e5c on `filetypes/python`

Cycle `20260606T092604-confirm-a8e6f3e5fa270e5c` — 2026-06-06T09:26:04Z

PR_AUC held across 3 seeds (orig 0.9958)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a8e6f3e5fa270e5c` | `0afcefc0421a7093` | `0afcefc0421a7093` | `0afcefc0421a7093` |
| PR AUC | 0.9958 | 0.9962 | 0.9958 | 0.9960 |
| ROC AUC | 0.9967 | 0.9970 | 0.9965 | 0.9968 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a8e6f3e5fa270e5c
```
