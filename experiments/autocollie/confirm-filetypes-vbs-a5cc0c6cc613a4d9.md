# Confirm PASS — a5cc0c6cc613a4d9 on `filetypes/vbs`

Cycle `20260613T011836-confirm-a5cc0c6cc613a4d9` — 2026-06-13T01:18:36Z

PR_AUC held across 3 seeds (orig 0.9980)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a5cc0c6cc613a4d9` | `691cc4f89efc4bb0` | `691cc4f89efc4bb0` | `691cc4f89efc4bb0` |
| PR AUC | 0.9980 | 0.9973 | 0.9977 | 0.9976 |
| ROC AUC | 0.9930 | 0.9902 | 0.9918 | 0.9915 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a5cc0c6cc613a4d9
```
