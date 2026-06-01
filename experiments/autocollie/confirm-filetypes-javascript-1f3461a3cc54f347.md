# Confirm PASS — 1f3461a3cc54f347 on `filetypes/javascript`

Cycle `20260601T204043-confirm-1f3461a3cc54f347` — 2026-06-01T20:40:43Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `1f3461a3cc54f347` | `feefa7844e1538f1` | `feefa7844e1538f1` | `feefa7844e1538f1` |
| PR AUC | 0.9994 | 0.9993 | 0.9993 | 0.9993 |
| ROC AUC | 0.9990 | 0.9990 | 0.9990 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=1f3461a3cc54f347
```
