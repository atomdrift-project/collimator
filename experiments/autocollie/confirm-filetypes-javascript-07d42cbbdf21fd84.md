# Confirm PASS — 07d42cbbdf21fd84 on `filetypes/javascript`

Cycle `20260521T052711-confirm-07d42cbbdf21fd84` — 2026-05-21T05:27:11Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `07d42cbbdf21fd84` | `e9e3cd72f928634f` | `e9e3cd72f928634f` | `e9e3cd72f928634f` |
| PR AUC | 0.9994 | 0.9997 | 0.9997 | 0.9997 |
| ROC AUC | 0.9989 | 0.9995 | 0.9995 | 0.9995 |
| Recall@3FPM | — | 0.8853 | 0.9058 | 0.8917 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=07d42cbbdf21fd84
```
