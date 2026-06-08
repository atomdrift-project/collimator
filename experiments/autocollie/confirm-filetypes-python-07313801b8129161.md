# Confirm PASS — 07313801b8129161 on `filetypes/python`

Cycle `20260608T182632-confirm-07313801b8129161` — 2026-06-08T18:26:32Z

PR_AUC held across 3 seeds (orig 0.9992)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `07313801b8129161` | `53ad72f688888765` | `53ad72f688888765` | `53ad72f688888765` |
| PR AUC | 0.9992 | 0.9943 | 0.9942 | 0.9943 |
| ROC AUC | 0.9993 | 0.9954 | 0.9953 | 0.9956 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=07313801b8129161
```
