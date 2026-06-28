# Confirm PASS — 29bc3becffabbf85 on `filetypes/crx`

Cycle `20260628T154540-confirm-29bc3becffabbf85` — 2026-06-28T15:45:40Z

PR_AUC held across 3 seeds (orig 0.9966)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `29bc3becffabbf85` | `a8a25b1387326ece` | `a8a25b1387326ece` | `a8a25b1387326ece` |
| PR AUC | 0.9966 | 0.9946 | 0.9944 | 0.9952 |
| ROC AUC | 0.9966 | 0.9946 | 0.9942 | 0.9953 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=29bc3becffabbf85
```
