# Confirm PASS — 6a515110d7bacb66 on `filetypes/macho`

Cycle `20260603T161211-confirm-6a515110d7bacb66` — 2026-06-03T16:12:11Z

PR_AUC held across 3 seeds (orig 0.9966)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6a515110d7bacb66` | `47ef7308185cf6bc` | `47ef7308185cf6bc` | `47ef7308185cf6bc` |
| PR AUC | 0.9966 | 0.9957 | 0.9955 | 0.9950 |
| ROC AUC | 0.9992 | 0.9990 | 0.9989 | 0.9988 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6a515110d7bacb66
```
