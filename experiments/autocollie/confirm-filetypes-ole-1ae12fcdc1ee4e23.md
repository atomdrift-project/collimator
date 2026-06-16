# Confirm PASS — 1ae12fcdc1ee4e23 on `filetypes/ole`

Cycle `20260616T052356-confirm-1ae12fcdc1ee4e23` — 2026-06-16T05:23:56Z

PR_AUC held across 3 seeds (orig 0.9957)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1ae12fcdc1ee4e23` | `59e0464da22b3744` | `59e0464da22b3744` | `59e0464da22b3744` |
| PR AUC | 0.9957 | 0.9955 | 0.9956 | 0.9959 |
| ROC AUC | 0.9946 | 0.9945 | 0.9948 | 0.9951 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1ae12fcdc1ee4e23
```
