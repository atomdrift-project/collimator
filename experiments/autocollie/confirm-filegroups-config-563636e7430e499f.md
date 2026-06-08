# Confirm PASS — 563636e7430e499f on `filegroups/config`

Cycle `20260608T121117-confirm-563636e7430e499f` — 2026-06-08T12:11:17Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `563636e7430e499f` | `2aab519bd42e3077` | `2aab519bd42e3077` | `2aab519bd42e3077` |
| PR AUC | 0.9988 | 0.9988 | 0.9987 | 0.9988 |
| ROC AUC | 0.9983 | 0.9983 | 0.9981 | 0.9982 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=563636e7430e499f
```
