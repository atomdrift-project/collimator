# Confirm PASS — 5edf7fe3e15cccf2 on `filetypes/python`

Cycle `20260712T234609-confirm-5edf7fe3e15cccf2` — 2026-07-12T23:46:09Z

PR_AUC held across 3 seeds (orig 0.9729)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5edf7fe3e15cccf2` | `31a49bd6dfdece11` | `31a49bd6dfdece11` | `31a49bd6dfdece11` |
| PR AUC | 0.9729 | 0.9789 | 0.9787 | 0.9785 |
| ROC AUC | 0.9875 | 0.9899 | 0.9897 | 0.9898 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=5edf7fe3e15cccf2
```
