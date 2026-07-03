# Confirm PASS — d927d17cc3b11904 on `filetypes/macho`

Cycle `20260703T003635-confirm-d927d17cc3b11904` — 2026-07-03T00:36:35Z

PR_AUC held across 3 seeds (orig 0.9951)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d927d17cc3b11904` | `a693643b31e0fdf1` | `a693643b31e0fdf1` | `a693643b31e0fdf1` |
| PR AUC | 0.9951 | 0.9937 | 0.9941 | 0.9940 |
| ROC AUC | 0.9989 | 0.9988 | 0.9988 | 0.9988 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d927d17cc3b11904
```
