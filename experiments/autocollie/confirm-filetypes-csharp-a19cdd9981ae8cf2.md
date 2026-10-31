# Confirm PASS — a19cdd9981ae8cf2 on `filetypes/csharp`

Cycle `20261031T000519-confirm-a19cdd9981ae8cf2` — 2026-10-31T00:05:19Z

averaged 3-seed ensemble PR_AUC held: 0.9611 -> 0.9701; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a19cdd9981ae8cf2` | `d5366e43b839dfa2` | `d5366e43b839dfa2` | `d5366e43b839dfa2` |
| PR AUC | 0.9611 | 0.9676 | 0.9714 | 0.9679 |
| ROC AUC | 0.9969 | 0.9974 | 0.9980 | 0.9967 |
| Recall@L50 | — | 0.3560 | 0.2576 | 0.3934 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a19cdd9981ae8cf2
```
