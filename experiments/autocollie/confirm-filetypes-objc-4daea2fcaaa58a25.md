# Confirm PASS — 4daea2fcaaa58a25 on `filetypes/objc`

Cycle `20260527T072841-confirm-4daea2fcaaa58a25` — 2026-05-27T07:28:41Z

PR_AUC held across 3 seeds (orig 0.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4daea2fcaaa58a25` | `d1cddd2c3aed7e99` | `d1cddd2c3aed7e99` | `d1cddd2c3aed7e99` |
| PR AUC | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| ROC AUC | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4daea2fcaaa58a25
```
