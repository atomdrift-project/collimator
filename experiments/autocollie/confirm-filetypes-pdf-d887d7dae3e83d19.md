# Confirm PASS — d887d7dae3e83d19 on `filetypes/pdf`

Cycle `20260703T011946-confirm-d887d7dae3e83d19` — 2026-07-03T01:19:46Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d887d7dae3e83d19` | `0a52d4d79b97b17d` | `0a52d4d79b97b17d` | `0a52d4d79b97b17d` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9985 | 0.9992 | 0.9988 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d887d7dae3e83d19
```
