# Confirm PASS — e788920478a0ad69 on `filetypes/macho`

Cycle `20260601T211237-confirm-e788920478a0ad69` — 2026-06-01T21:12:37Z

PR_AUC held across 3 seeds (orig 0.9992)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e788920478a0ad69` | `5f798cfa0d934d96` | `5f798cfa0d934d96` | `5f798cfa0d934d96` |
| PR AUC | 0.9992 | 0.9961 | 0.9963 | 0.9964 |
| ROC AUC | 0.9998 | 0.9990 | 0.9991 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e788920478a0ad69
```
