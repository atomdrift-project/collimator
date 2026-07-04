# Confirm PASS — 38a40f477c53f8e9 on `filetypes/xls`

Cycle `20260704T190523-confirm-38a40f477c53f8e9` — 2026-07-04T19:05:23Z

PR_AUC held across 3 seeds (orig 0.9972)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `38a40f477c53f8e9` | `8295573a5639df11` | `8295573a5639df11` | `8295573a5639df11` |
| PR AUC | 0.9972 | 0.9977 | 0.9977 | 0.9975 |
| ROC AUC | 0.9915 | 0.9926 | 0.9924 | 0.9918 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=38a40f477c53f8e9
```
