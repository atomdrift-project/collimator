# Confirm PASS — b38aff58277abb5d on `filetypes/csharp`

Cycle `20260609T095746-confirm-b38aff58277abb5d` — 2026-06-09T09:57:46Z

PR_AUC held across 3 seeds (orig 0.9930)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b38aff58277abb5d` | `a0fc7d9b02c0196e` | `a0fc7d9b02c0196e` | `a0fc7d9b02c0196e` |
| PR AUC | 0.9930 | 0.9912 | 0.9902 | 0.9907 |
| ROC AUC | 0.9950 | 0.9936 | 0.9929 | 0.9934 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b38aff58277abb5d
```
