# Confirm PASS — 07313801b8129161 on `filetypes/python`

Cycle `20260602T012437-confirm-07313801b8129161` — 2026-06-02T01:24:37Z

PR_AUC held across 3 seeds (orig 0.9992)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `07313801b8129161` | `674abd9208bae962` | `674abd9208bae962` | `674abd9208bae962` |
| PR AUC | 0.9992 | 0.9972 | 0.9975 | 0.9973 |
| ROC AUC | 0.9993 | 0.9979 | 0.9982 | 0.9980 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=07313801b8129161
```
