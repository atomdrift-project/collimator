# Confirm PASS — cad3a137090e6b9f on `filetypes/shell`

Cycle `20260614T013954-confirm-cad3a137090e6b9f` — 2026-06-14T01:39:54Z

PR_AUC held across 3 seeds (orig 0.9960)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cad3a137090e6b9f` | `104a497cdd402e94` | `104a497cdd402e94` | `104a497cdd402e94` |
| PR AUC | 0.9960 | 0.9974 | 0.9974 | 0.9976 |
| ROC AUC | 0.9974 | 0.9975 | 0.9976 | 0.9977 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cad3a137090e6b9f
```
