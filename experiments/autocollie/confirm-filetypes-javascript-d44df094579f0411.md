# Confirm PASS — d44df094579f0411 on `filetypes/javascript`

Cycle `20260711T153618-confirm-d44df094579f0411` — 2026-07-11T15:36:18Z

PR_AUC held across 3 seeds (orig 0.9950)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d44df094579f0411` | `fbcf8096f3cfeee0` | `fbcf8096f3cfeee0` | `fbcf8096f3cfeee0` |
| PR AUC | 0.9950 | 0.9963 | 0.9963 | 0.9962 |
| ROC AUC | 0.9941 | 0.9969 | 0.9969 | 0.9968 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d44df094579f0411
```
