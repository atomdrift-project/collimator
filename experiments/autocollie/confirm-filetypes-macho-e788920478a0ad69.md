# Confirm PASS — e788920478a0ad69 on `filetypes/macho`

Cycle `20260525T202922-confirm-e788920478a0ad69` — 2026-05-25T20:29:22Z

PR_AUC held across 3 seeds (orig 0.9992)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e788920478a0ad69` | `9b215c3126a94421` | `9b215c3126a94421` | `9b215c3126a94421` |
| PR AUC | 0.9992 | 0.9977 | 0.9974 | 0.9972 |
| ROC AUC | 0.9998 | 0.9995 | 0.9995 | 0.9994 |
| Recall@3FPM | — | 0.9098 | 0.8759 | 0.8947 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e788920478a0ad69
```
