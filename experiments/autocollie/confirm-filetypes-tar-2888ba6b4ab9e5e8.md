# Confirm PASS — 2888ba6b4ab9e5e8 on `filetypes/tar`

Cycle `20260608T161258-confirm-2888ba6b4ab9e5e8` — 2026-06-08T16:12:58Z

PR_AUC held across 3 seeds (orig 0.9968)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2888ba6b4ab9e5e8` | `9deb7a8e9d342a6c` | `9deb7a8e9d342a6c` | `9deb7a8e9d342a6c` |
| PR AUC | 0.9968 | 0.9973 | 0.9966 | 0.9965 |
| ROC AUC | 0.9894 | 0.9912 | 0.9885 | 0.9882 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2888ba6b4ab9e5e8
```
