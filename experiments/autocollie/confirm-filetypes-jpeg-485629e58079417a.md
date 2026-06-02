# Confirm PASS — 485629e58079417a on `filetypes/jpeg`

Cycle `20260602T025837-confirm-485629e58079417a` — 2026-06-02T02:58:37Z

PR_AUC held across 3 seeds (orig 0.9692)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `485629e58079417a` | `b35c23bdf8c1b4db` | `b35c23bdf8c1b4db` | `b35c23bdf8c1b4db` |
| PR AUC | 0.9692 | 0.9692 | 0.9624 | 0.9696 |
| ROC AUC | 0.9832 | 0.9832 | 0.9804 | 0.9836 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=485629e58079417a
```
