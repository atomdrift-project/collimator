# Confirm PASS — 39e529347cd04596 on `filetypes/static-lib`

Cycle `20261029T034408-confirm-39e529347cd04596` — 2026-10-29T03:44:08Z

PR_AUC held across 3 seeds (orig 0.5912)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `39e529347cd04596` | `d98fd3fe57bdc91b` | `d98fd3fe57bdc91b` | `d98fd3fe57bdc91b` |
| PR AUC | 0.5912 | 0.6145 | 0.6326 | 0.6253 |
| ROC AUC | 0.8767 | 0.8959 | 0.9079 | 0.9002 |
| Recall@L50 | — | 0.3308 | 0.3000 | 0.3346 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=39e529347cd04596
```
