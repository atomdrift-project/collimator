# Confirm PASS — d51a3eac8476b247 on `filetypes/shell`

Cycle `20260528T083549-confirm-d51a3eac8476b247` — 2026-05-28T08:35:49Z

PR_AUC held across 3 seeds (orig 0.9960)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d51a3eac8476b247` | `18021b21c57387ac` | `18021b21c57387ac` | `18021b21c57387ac` |
| PR AUC | 0.9960 | 0.9966 | 0.9968 | 0.9962 |
| ROC AUC | 0.9974 | 0.9978 | 0.9979 | 0.9975 |
| Recall@3FPM | — | 0.8630 | 0.8876 | 0.8597 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d51a3eac8476b247
```
