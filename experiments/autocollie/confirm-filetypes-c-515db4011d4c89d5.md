# Confirm PASS — 515db4011d4c89d5 on `filetypes/c`

Cycle `20260601T145701-confirm-515db4011d4c89d5` — 2026-06-01T14:57:01Z

PR_AUC held across 3 seeds (orig 0.9909)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `515db4011d4c89d5` | `734f56e86c6d78f0` | `734f56e86c6d78f0` | `734f56e86c6d78f0` |
| PR AUC | 0.9909 | 0.9886 | 0.9906 | 0.9887 |
| ROC AUC | 0.9950 | 0.9944 | 0.9956 | 0.9941 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=515db4011d4c89d5
```
