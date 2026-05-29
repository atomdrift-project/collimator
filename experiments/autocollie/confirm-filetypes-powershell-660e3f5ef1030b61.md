# Confirm PASS — 660e3f5ef1030b61 on `filetypes/powershell`

Cycle `20260527T011314-confirm-660e3f5ef1030b61` — 2026-05-27T01:13:14Z

PR_AUC held across 3 seeds (orig 0.9986)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `660e3f5ef1030b61` | `5e06992ff8a4959e` | `5e06992ff8a4959e` | `5e06992ff8a4959e` |
| PR AUC | 0.9986 | 0.9985 | 0.9990 | 0.9983 |
| ROC AUC | 0.9966 | 0.9951 | 0.9967 | 0.9943 |
| Recall@3FPM | — | 0.8262 | 0.8319 | 0.7578 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=660e3f5ef1030b61
```
