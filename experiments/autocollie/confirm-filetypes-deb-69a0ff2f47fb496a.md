# Confirm PASS — 69a0ff2f47fb496a on `filetypes/deb`

Cycle `20261031T005226-confirm-69a0ff2f47fb496a` — 2026-10-31T00:52:26Z

averaged 3-seed ensemble PR_AUC held: 0.1093 -> 0.2093; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `69a0ff2f47fb496a` | `eff1e47ed6231660` | `eff1e47ed6231660` | `eff1e47ed6231660` |
| PR AUC | 0.1093 | 0.1812 | 0.1880 | 0.2145 |
| ROC AUC | 0.6579 | 0.8648 | 0.8573 | 0.6322 |
| Recall@L50 | — | 0.1333 | 0.1333 | 0.2000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=69a0ff2f47fb496a
```
