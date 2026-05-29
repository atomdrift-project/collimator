# Confirm PASS — e9cac950d37beb8f on `filetypes/plist`

Cycle `20260527T062853-confirm-e9cac950d37beb8f` — 2026-05-27T06:28:53Z

PR_AUC held across 3 seeds (orig 0.2000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e9cac950d37beb8f` | `b61be3df21f9d2d5` | `b61be3df21f9d2d5` | `b61be3df21f9d2d5` |
| PR AUC | 0.2000 | 0.2000 | 0.2000 | 0.2000 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e9cac950d37beb8f
```
