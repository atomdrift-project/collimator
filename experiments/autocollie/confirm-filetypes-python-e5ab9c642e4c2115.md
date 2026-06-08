# Confirm PASS — e5ab9c642e4c2115 on `filetypes/python`

Cycle `20260608T182736-confirm-e5ab9c642e4c2115` — 2026-06-08T18:27:36Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e5ab9c642e4c2115` | `2cde5a0ba94f06b5` | `2cde5a0ba94f06b5` | `2cde5a0ba94f06b5` |
| PR AUC | 0.9990 | 0.9939 | 0.9943 | 0.9941 |
| ROC AUC | 0.9990 | 0.9949 | 0.9954 | 0.9952 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e5ab9c642e4c2115
```
