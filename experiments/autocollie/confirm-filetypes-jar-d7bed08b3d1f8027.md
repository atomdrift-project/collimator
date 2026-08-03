# Confirm PASS — d7bed08b3d1f8027 on `filetypes/jar`

Cycle `20260723T062103-confirm-d7bed08b3d1f8027` — 2026-07-23T06:21:03Z

PR_AUC held across 3 seeds (orig 0.9821)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d7bed08b3d1f8027` | `93e6bc1a1b7c8a51` | `93e6bc1a1b7c8a51` | `93e6bc1a1b7c8a51` |
| PR AUC | 0.9821 | 0.9885 | 0.9857 | 0.9833 |
| ROC AUC | 0.9827 | 0.9884 | 0.9859 | 0.9843 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d7bed08b3d1f8027
```
