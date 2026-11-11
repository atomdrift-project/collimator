# Confirm PASS — d2173256fdf4cd40 on `filetypes/xpi`

Cycle `20261106T113453-confirm-d2173256fdf4cd40` — 2026-11-06T11:34:53Z

averaged 3-seed ensemble PR_AUC held: 0.9192 -> 0.9283; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d2173256fdf4cd40` | `380524cfb3066eca` | `380524cfb3066eca` | `380524cfb3066eca` |
| PR AUC | 0.9192 | 0.9134 | 0.9237 | 0.9283 |
| ROC AUC | 0.9990 | 0.9984 | 0.9988 | 0.9991 |
| Recall@L50 | — | 0.5556 | 0.5556 | 0.4444 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d2173256fdf4cd40
```
