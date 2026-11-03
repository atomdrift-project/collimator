# Confirm PASS — 8d7ea96a3a5834d1 on `filetypes/macho`

Cycle `20261102T190547-confirm-8d7ea96a3a5834d1` — 2026-11-02T19:05:47Z

averaged 3-seed ensemble PR_AUC held: 0.9881 -> 0.9896; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8d7ea96a3a5834d1` | `721d9dd5e82d351e` | `721d9dd5e82d351e` | `721d9dd5e82d351e` |
| PR AUC | 0.9881 | 0.9901 | 0.9860 | 0.9889 |
| ROC AUC | 0.9988 | 0.9989 | 0.9984 | 0.9989 |
| Recall@L50 | — | 0.7851 | 0.7321 | 0.7162 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8d7ea96a3a5834d1
```
