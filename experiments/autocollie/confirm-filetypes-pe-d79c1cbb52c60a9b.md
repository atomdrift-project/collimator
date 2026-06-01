# Confirm PASS — d79c1cbb52c60a9b on `filetypes/pe`

Cycle `20260601T201801-confirm-d79c1cbb52c60a9b` — 2026-06-01T20:18:01Z

PR_AUC held across 3 seeds (orig 0.9997)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d79c1cbb52c60a9b` | `7057be53b5900666` | `7057be53b5900666` | `7057be53b5900666` |
| PR AUC | 0.9997 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9997 | 0.9999 | 0.9999 | 0.9999 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d79c1cbb52c60a9b
```
