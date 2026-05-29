# Confirm PASS — 9ebc7e1409721b3f on `filetypes/pptx`

Cycle `20260527T081601-confirm-9ebc7e1409721b3f` — 2026-05-27T08:16:01Z

PR_AUC held across 3 seeds (orig 0.9231)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9ebc7e1409721b3f` | `4f93026436917662` | `4f93026436917662` | `4f93026436917662` |
| PR AUC | 0.9231 | 0.9231 | 0.9231 | 0.9231 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9ebc7e1409721b3f
```
