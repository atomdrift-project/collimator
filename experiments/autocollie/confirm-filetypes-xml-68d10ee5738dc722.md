# Confirm PASS — 68d10ee5738dc722 on `filetypes/xml`

Cycle `20260616T050636-confirm-68d10ee5738dc722` — 2026-06-16T05:06:36Z

PR_AUC held across 3 seeds (orig 0.9982)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `68d10ee5738dc722` | `fcb2c990e9ddbb08` | `fcb2c990e9ddbb08` | `fcb2c990e9ddbb08` |
| PR AUC | 0.9982 | 0.9968 | 0.9982 | 0.9965 |
| ROC AUC | 0.9995 | 0.9991 | 0.9995 | 0.9989 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=68d10ee5738dc722
```
