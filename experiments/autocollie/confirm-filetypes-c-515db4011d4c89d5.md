# Confirm PASS — 515db4011d4c89d5 on `filetypes/c`

Cycle `20260528T011251-confirm-515db4011d4c89d5` — 2026-05-28T01:12:51Z

PR_AUC held across 3 seeds (orig 0.9909)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `515db4011d4c89d5` | `7935e1f50aa30685` | `7935e1f50aa30685` | `7935e1f50aa30685` |
| PR AUC | 0.9909 | 0.9912 | 0.9904 | 0.9912 |
| ROC AUC | 0.9950 | 0.9956 | 0.9947 | 0.9954 |
| Recall@3FPM | — | 0.7897 | 0.8054 | 0.8031 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=515db4011d4c89d5
```
