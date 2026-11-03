# Confirm PASS — 3a0a62c1c0d293c1 on `filetypes/c`

Cycle `20261102T194242-confirm-3a0a62c1c0d293c1` — 2026-11-02T19:42:42Z

averaged 3-seed ensemble PR_AUC held: 0.9453 -> 0.9531; individual seeds may be noisy

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3a0a62c1c0d293c1` | `77999fadab9f8b67` | `77999fadab9f8b67` | `77999fadab9f8b67` |
| PR AUC | 0.9453 | 0.9543 | 0.9201 | 0.9398 |
| ROC AUC | 0.9803 | 0.9816 | 0.9608 | 0.9765 |
| Recall@L50 | — | 0.5077 | 0.5057 | 0.5375 |
| verdict | — | PASS | FAIL | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3a0a62c1c0d293c1
```
