# Confirm PASS — d823fdd6a37fa191 on `filetypes/php`

Cycle `20260614T023959-confirm-d823fdd6a37fa191` — 2026-06-14T02:39:59Z

PR_AUC held across 3 seeds (orig 0.9921)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d823fdd6a37fa191` | `3f3921bbab4026d6` | `3f3921bbab4026d6` | `3f3921bbab4026d6` |
| PR AUC | 0.9921 | 0.9947 | 0.9946 | 0.9951 |
| ROC AUC | 0.9959 | 0.9975 | 0.9974 | 0.9976 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d823fdd6a37fa191
```
