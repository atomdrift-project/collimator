# Confirm PASS — e5c5747824a31661 on `filetypes/javascript`

Cycle `20260521T062904-confirm-e5c5747824a31661` — 2026-05-21T06:29:04Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e5c5747824a31661` | `d7b085be65e6acd7` | `d7b085be65e6acd7` | `d7b085be65e6acd7` |
| PR AUC | 0.9994 | 0.9997 | 0.9997 | 0.9997 |
| ROC AUC | 0.9990 | 0.9995 | 0.9995 | 0.9995 |
| Recall@3FPM | — | 0.9029 | 0.8982 | 0.9033 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e5c5747824a31661
```
