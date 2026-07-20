# Confirm PASS — f1248e94c679230d on `filetypes/package.json`

Cycle `20260720T114756-confirm-f1248e94c679230d` — 2026-07-20T11:47:56Z

PR_AUC held across 3 seeds (orig 0.9981)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f1248e94c679230d` | `0fa466c29b4bb754` | `0fa466c29b4bb754` | `0fa466c29b4bb754` |
| PR AUC | 0.9981 | 0.9982 | 0.9983 | 0.9983 |
| ROC AUC | 0.9984 | 0.9984 | 0.9985 | 0.9986 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f1248e94c679230d
```
