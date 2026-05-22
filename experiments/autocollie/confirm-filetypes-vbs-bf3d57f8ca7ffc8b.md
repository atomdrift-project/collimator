# Confirm PASS — bf3d57f8ca7ffc8b on `filetypes/vbs`

Cycle `20260522T172252-confirm-bf3d57f8ca7ffc8b` — 2026-05-22T17:22:52Z

PR_AUC held across 3 seeds (orig 0.9979)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bf3d57f8ca7ffc8b` | `2d1bd72d1a70409f` | `2d1bd72d1a70409f` | `2d1bd72d1a70409f` |
| PR AUC | 0.9979 | 0.9974 | 0.9981 | 0.9979 |
| ROC AUC | 0.9853 | 0.9836 | 0.9866 | 0.9858 |
| Recall@3FPM | — | 0.5206 | 0.6675 | 0.6366 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bf3d57f8ca7ffc8b
```
