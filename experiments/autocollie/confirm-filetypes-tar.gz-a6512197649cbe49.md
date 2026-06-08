# Confirm PASS — a6512197649cbe49 on `filetypes/tar.gz`

Cycle `20260608T110430-confirm-a6512197649cbe49` — 2026-06-08T11:04:30Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a6512197649cbe49` | `7b7fe74c2d6db170` | `7b7fe74c2d6db170` | `7b7fe74c2d6db170` |
| PR AUC | 0.9993 | 0.9994 | 0.9994 | 0.9994 |
| ROC AUC | 0.9986 | 0.9987 | 0.9987 | 0.9988 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=a6512197649cbe49
```
