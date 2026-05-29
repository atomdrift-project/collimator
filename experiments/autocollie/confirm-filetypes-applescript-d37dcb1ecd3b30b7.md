# Confirm PASS — d37dcb1ecd3b30b7 on `filetypes/applescript`

Cycle `20260527T065028-confirm-d37dcb1ecd3b30b7` — 2026-05-27T06:50:28Z

PR_AUC held across 3 seeds (orig 0.4000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d37dcb1ecd3b30b7` | `1dabf901b8f57d04` | `1dabf901b8f57d04` | `1dabf901b8f57d04` |
| PR AUC | 0.4000 | 0.4000 | 0.4000 | 0.4000 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d37dcb1ecd3b30b7
```
