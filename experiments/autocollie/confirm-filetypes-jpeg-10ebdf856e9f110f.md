# Confirm PASS — 10ebdf856e9f110f on `filetypes/jpeg`

Cycle `20260713T214345-confirm-10ebdf856e9f110f` — 2026-07-13T21:43:45Z

PR_AUC held across 3 seeds (orig 0.9768)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `10ebdf856e9f110f` | `b08d22467a8b67f7` | `b08d22467a8b67f7` | `b08d22467a8b67f7` |
| PR AUC | 0.9768 | 0.9759 | 0.9780 | 0.9791 |
| ROC AUC | 0.9755 | 0.9762 | 0.9787 | 0.9793 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=10ebdf856e9f110f
```
