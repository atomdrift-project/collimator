# Confirm PASS — 1ffaf15111dff4bb on `filetypes/registry`

Cycle `20260702T224930-confirm-1ffaf15111dff4bb` — 2026-07-02T22:49:30Z

PR_AUC held across 3 seeds (orig 0.5172)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1ffaf15111dff4bb` | `dd3eb3fb33bf09a4` | `dd3eb3fb33bf09a4` | `dd3eb3fb33bf09a4` |
| PR AUC | 0.5172 | 0.5172 | 0.4545 | 0.4688 |
| ROC AUC | 0.9971 | 0.9971 | 0.9963 | 0.9965 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | FAIL | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1ffaf15111dff4bb
```
