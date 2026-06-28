# Confirm PASS — 3d27f2362f791915 on `filegroups/media`

Cycle `20260628T104258-confirm-3d27f2362f791915` — 2026-06-28T10:42:58Z

PR_AUC held across 3 seeds (orig 0.9870)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3d27f2362f791915` | `f0980c102926b45f` | `f0980c102926b45f` | `f0980c102926b45f` |
| PR AUC | 0.9870 | 0.9851 | 0.9883 | 0.9846 |
| ROC AUC | 0.9858 | 0.9838 | 0.9869 | 0.9820 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3d27f2362f791915
```
