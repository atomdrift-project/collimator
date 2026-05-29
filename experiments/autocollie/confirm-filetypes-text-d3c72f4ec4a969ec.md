# Confirm PASS — d3c72f4ec4a969ec on `filetypes/text`

Cycle `20260527T014900-confirm-d3c72f4ec4a969ec` — 2026-05-27T01:49:00Z

PR_AUC held across 3 seeds (orig 0.9691)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d3c72f4ec4a969ec` | `11c286aa40fc20dc` | `11c286aa40fc20dc` | `11c286aa40fc20dc` |
| PR AUC | 0.9691 | 0.9581 | 0.9740 | 0.9649 |
| ROC AUC | 0.9851 | 0.9826 | 0.9881 | 0.9808 |
| Recall@3FPM | — | 0.6190 | 0.8095 | 0.8571 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d3c72f4ec4a969ec
```
