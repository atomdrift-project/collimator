# Confirm PASS — d190a9219e984981 on `filetypes/msi`

Cycle `20260526T220034-confirm-d190a9219e984981` — 2026-05-26T22:00:34Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d190a9219e984981` | `09c905a98a4b427f` | `09c905a98a4b427f` | `09c905a98a4b427f` |
| PR AUC | 0.9999 | 0.9999 | 0.9999 | 0.9999 |
| ROC AUC | 0.9990 | 0.9967 | 0.9967 | 0.9973 |
| Recall@3FPM | — | 0.9867 | 0.9867 | 0.9900 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d190a9219e984981
```
