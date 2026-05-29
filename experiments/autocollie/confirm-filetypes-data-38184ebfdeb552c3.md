# Confirm PASS — 38184ebfdeb552c3 on `filetypes/data`

Cycle `20260526T205824-confirm-38184ebfdeb552c3` — 2026-05-26T20:58:24Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `38184ebfdeb552c3` | `b4c127bfc6ea4786` | `b4c127bfc6ea4786` | `b4c127bfc6ea4786` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=38184ebfdeb552c3
```
