# Confirm PASS — d3569d2c0c3a15f1 on `filetypes/gem`

Cycle `20260824T212347-confirm-d3569d2c0c3a15f1` — 2026-08-24T21:23:47Z

PR_AUC held across 3 seeds (orig 0.9902)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d3569d2c0c3a15f1` | `cb7e250990a5f3a6` | `cb7e250990a5f3a6` | `cb7e250990a5f3a6` |
| PR AUC | 0.9902 | 0.9878 | 0.9847 | 0.9871 |
| ROC AUC | 0.9955 | 0.9923 | 0.9898 | 0.9927 |
| Recall@L50 | — | 0.9636 | 0.9636 | 0.9636 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d3569d2c0c3a15f1
```
