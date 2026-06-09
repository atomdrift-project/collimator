# Confirm PASS — d0f3777b30bd6677 on `filetypes/png`

Cycle `20260609T050308-confirm-d0f3777b30bd6677` — 2026-06-09T05:03:08Z

PR_AUC held across 3 seeds (orig 0.9785)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d0f3777b30bd6677` | `50977ddd2f88ca75` | `50977ddd2f88ca75` | `50977ddd2f88ca75` |
| PR AUC | 0.9785 | 0.9748 | 0.9764 | 0.9806 |
| ROC AUC | 0.9710 | 0.9644 | 0.9665 | 0.9734 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d0f3777b30bd6677
```
