# Confirm PASS — 1a85596b8ef05b8c on `filetypes/ico`

Cycle `20261029T024813-confirm-1a85596b8ef05b8c` — 2026-10-29T02:48:13Z

PR_AUC held across 3 seeds (orig 0.8399)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1a85596b8ef05b8c` | `a23b26f85f9f72d5` | `a23b26f85f9f72d5` | `a23b26f85f9f72d5` |
| PR AUC | 0.8399 | 0.7677 | 0.8399 | 0.7677 |
| ROC AUC | 0.9223 | 0.8485 | 0.9209 | 0.8485 |
| Recall@L50 | — | 0.7000 | 0.7000 | 0.7000 |
| verdict | — | FAIL | PASS | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1a85596b8ef05b8c
```
