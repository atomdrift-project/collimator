# Confirm PASS — 58862d3b580739a1 on `filetypes/shell`

Cycle `20260525T211511-confirm-58862d3b580739a1` — 2026-05-25T21:15:11Z

PR_AUC held across 3 seeds (orig 0.9984)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `58862d3b580739a1` | `d608181d89775b70` | `d608181d89775b70` | `d608181d89775b70` |
| PR AUC | 0.9984 | 0.9972 | 0.9973 | 0.9973 |
| ROC AUC | 0.9995 | 0.9980 | 0.9982 | 0.9981 |
| Recall@3FPM | — | 0.8863 | 0.8552 | 0.8906 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=58862d3b580739a1
```
