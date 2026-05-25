# Confirm PASS — a78991a84e733747 on `filetypes/c`

Cycle `20260524T150023-confirm-a78991a84e733747` — 2026-05-24T15:00:23Z

PR_AUC held across 3 seeds (orig 0.9922)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a78991a84e733747` | `7788f1171ed5927b` | `7788f1171ed5927b` | `7788f1171ed5927b` |
| PR AUC | 0.9922 | 0.9916 | 0.9916 | 0.9914 |
| ROC AUC | 0.9958 | 0.9956 | 0.9955 | 0.9955 |
| Recall@3FPM | — | 0.7593 | 0.7801 | 0.7824 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a78991a84e733747
```
