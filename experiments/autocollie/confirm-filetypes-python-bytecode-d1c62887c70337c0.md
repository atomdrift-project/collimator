# Confirm PASS — d1c62887c70337c0 on `filetypes/python-bytecode`

Cycle `20260526T225219-confirm-d1c62887c70337c0` — 2026-05-26T22:52:19Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d1c62887c70337c0` | `0391bd501688ba8e` | `0391bd501688ba8e` | `0391bd501688ba8e` |
| PR AUC | 0.9996 | 0.9983 | 0.9982 | 0.9987 |
| ROC AUC | 0.9974 | 0.9930 | 0.9927 | 0.9948 |
| Recall@3FPM | — | 0.8939 | 0.8857 | 0.9224 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d1c62887c70337c0
```
