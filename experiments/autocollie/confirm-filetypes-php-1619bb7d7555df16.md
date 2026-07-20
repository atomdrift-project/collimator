# Confirm PASS — 1619bb7d7555df16 on `filetypes/php`

Cycle `20260715T073557-confirm-1619bb7d7555df16` — 2026-07-15T07:35:57Z

PR_AUC held across 3 seeds (orig 0.9839)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1619bb7d7555df16` | `45a259d91c51b0ee` | `45a259d91c51b0ee` | `45a259d91c51b0ee` |
| PR AUC | 0.9839 | 0.9839 | 0.9841 | 0.9840 |
| ROC AUC | 0.9960 | 0.9950 | 0.9955 | 0.9957 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1619bb7d7555df16
```
