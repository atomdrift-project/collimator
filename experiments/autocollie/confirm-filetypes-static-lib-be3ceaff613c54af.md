# Confirm PASS — be3ceaff613c54af on `filetypes/static-lib`

Cycle `20261029T131157-confirm-be3ceaff613c54af` — 2026-10-29T13:11:57Z

averaged 3-seed ensemble PR_AUC held: 0.5939 -> 0.6192; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `be3ceaff613c54af` | `873cd36d00ffb24e` | `873cd36d00ffb24e` | `873cd36d00ffb24e` |
| PR AUC | 0.5939 | 0.6157 | 0.6329 | 0.6218 |
| ROC AUC | 0.8788 | 0.8997 | 0.9069 | 0.9002 |
| Recall@L50 | — | 0.3308 | 0.3000 | 0.3346 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=be3ceaff613c54af
```
