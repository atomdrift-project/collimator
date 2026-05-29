# Confirm PASS — 63d67e385bcc6ca0 on `filetypes/plist`

Cycle `20260527T062520-confirm-63d67e385bcc6ca0` — 2026-05-27T06:25:20Z

PR_AUC held across 3 seeds (orig 0.2000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `63d67e385bcc6ca0` | `e76b5b8f5f2213e3` | `e76b5b8f5f2213e3` | `e76b5b8f5f2213e3` |
| PR AUC | 0.2000 | 0.2000 | 0.2000 | 0.2000 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=63d67e385bcc6ca0
```
