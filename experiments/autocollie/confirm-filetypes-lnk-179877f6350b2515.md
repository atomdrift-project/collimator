# Confirm PASS — 179877f6350b2515 on `filetypes/lnk`

Cycle `20260608T022137-confirm-179877f6350b2515` — 2026-06-08T02:21:37Z

PR_AUC held across 3 seeds (orig 0.9952)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `179877f6350b2515` | `4854f3f4401bcf35` | `4854f3f4401bcf35` | `4854f3f4401bcf35` |
| PR AUC | 0.9952 | 0.9954 | 0.9958 | 0.9957 |
| ROC AUC | 0.9792 | 0.9796 | 0.9808 | 0.9811 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=179877f6350b2515
```
