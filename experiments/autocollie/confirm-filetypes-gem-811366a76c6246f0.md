# Confirm PASS — 811366a76c6246f0 on `filetypes/gem`

Cycle `20260627T123525-confirm-811366a76c6246f0` — 2026-06-27T12:35:25Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `811366a76c6246f0` | `37bda1216ac2a83f` | `37bda1216ac2a83f` | `37bda1216ac2a83f` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=811366a76c6246f0
```
