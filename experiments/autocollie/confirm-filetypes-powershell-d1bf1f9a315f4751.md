# Confirm PASS — d1bf1f9a315f4751 on `filetypes/powershell`

Cycle `20260521T073218-confirm-d1bf1f9a315f4751` — 2026-05-21T07:32:18Z

PR_AUC held across 3 seeds (orig 0.9984)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d1bf1f9a315f4751` | `d5c1a7e22148e488` | `d5c1a7e22148e488` | `d5c1a7e22148e488` |
| PR AUC | 0.9984 | 0.9968 | 0.9987 | 0.9965 |
| ROC AUC | 0.9961 | 0.9925 | 0.9967 | 0.9923 |
| Recall@3FPM | — | 0.7339 | 0.8589 | 0.6210 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d1bf1f9a315f4751
```
