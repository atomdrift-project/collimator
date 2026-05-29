# Confirm PASS — 1ae14bbd1c829872 on `filetypes/lua`

Cycle `20260527T052831-confirm-1ae14bbd1c829872` — 2026-05-27T05:28:31Z

PR_AUC held across 3 seeds (orig 0.5995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1ae14bbd1c829872` | `4265126117ff70fc` | `4265126117ff70fc` | `4265126117ff70fc` |
| PR AUC | 0.5995 | 0.7183 | 0.7056 | 0.7056 |
| ROC AUC | 0.7772 | 0.9076 | 0.8315 | 0.8641 |
| Recall@3FPM | — | 0.5000 | 0.5000 | 0.5000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1ae14bbd1c829872
```
