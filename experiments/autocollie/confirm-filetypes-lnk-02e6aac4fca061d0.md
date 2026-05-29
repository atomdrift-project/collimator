# Confirm PASS — 02e6aac4fca061d0 on `filetypes/lnk`

Cycle `20260526T234326-confirm-02e6aac4fca061d0` — 2026-05-26T23:43:26Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `02e6aac4fca061d0` | `c55350027c1622d2` | `c55350027c1622d2` | `c55350027c1622d2` |
| PR AUC | 0.9988 | 0.9987 | 0.9990 | 0.9989 |
| ROC AUC | 0.9855 | 0.9829 | 0.9870 | 0.9860 |
| Recall@3FPM | — | 0.9282 | 0.9590 | 0.9487 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=02e6aac4fca061d0
```
