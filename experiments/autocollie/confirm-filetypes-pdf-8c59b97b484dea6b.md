# Confirm PASS — 8c59b97b484dea6b on `filetypes/pdf`

Cycle `20260601T125822-confirm-8c59b97b484dea6b` — 2026-06-01T12:58:22Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8c59b97b484dea6b` | `3098726c5f4d31d3` | `3098726c5f4d31d3` | `3098726c5f4d31d3` |
| PR AUC | 1.0000 | 0.9999 | 0.9991 | 0.9998 |
| ROC AUC | 0.9992 | 0.9921 | 0.9513 | 0.9886 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8c59b97b484dea6b
```
