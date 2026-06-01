# Confirm PASS — d51a3eac8476b247 on `filetypes/shell`

Cycle `20260601T141117-confirm-d51a3eac8476b247` — 2026-06-01T14:11:17Z

PR_AUC held across 3 seeds (orig 0.9960)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d51a3eac8476b247` | `ae36794263b81f9f` | `ae36794263b81f9f` | `ae36794263b81f9f` |
| PR AUC | 0.9960 | 0.9987 | 0.9985 | 0.9985 |
| ROC AUC | 0.9974 | 0.9988 | 0.9986 | 0.9986 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d51a3eac8476b247
```
