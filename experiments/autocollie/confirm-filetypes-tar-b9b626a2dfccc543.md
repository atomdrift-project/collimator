# Confirm PASS — b9b626a2dfccc543 on `filetypes/tar`

Cycle `20260526T212737-confirm-b9b626a2dfccc543` — 2026-05-26T21:27:37Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b9b626a2dfccc543` | `e413690766a95833` | `e413690766a95833` | `e413690766a95833` |
| PR AUC | 1.0000 | 0.9997 | 0.9993 | 0.9997 |
| ROC AUC | 1.0000 | 0.9974 | 0.9934 | 0.9971 |
| Recall@3FPM | — | 0.9803 | 0.9868 | 0.9737 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b9b626a2dfccc543
```
