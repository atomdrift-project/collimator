# Confirm PASS — 8bd52a3b2450ee60 on `filetypes/csharp`

Cycle `20260527T003023-confirm-8bd52a3b2450ee60` — 2026-05-27T00:30:23Z

PR_AUC held across 3 seeds (orig 0.9882)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8bd52a3b2450ee60` | `97935a46ec8491ad` | `97935a46ec8491ad` | `97935a46ec8491ad` |
| PR AUC | 0.9882 | 0.9845 | 0.9834 | 0.9879 |
| ROC AUC | 0.9937 | 0.9915 | 0.9902 | 0.9934 |
| Recall@3FPM | — | 0.8028 | 0.8732 | 0.9155 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8bd52a3b2450ee60
```
