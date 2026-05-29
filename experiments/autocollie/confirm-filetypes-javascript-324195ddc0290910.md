# Confirm PASS — 324195ddc0290910 on `filetypes/javascript`

Cycle `20260526T065615-confirm-324195ddc0290910` — 2026-05-26T06:56:15Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `324195ddc0290910` | `b82523545518fc37` | `b82523545518fc37` | `b82523545518fc37` |
| PR AUC | 0.9994 | 0.9997 | 0.9997 | 0.9996 |
| ROC AUC | 0.9990 | 0.9995 | 0.9995 | 0.9995 |
| Recall@3FPM | — | 0.8836 | 0.8869 | 0.8800 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=324195ddc0290910
```
