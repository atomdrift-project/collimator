# Confirm PASS — 023687eb694076df on `filetypes/javascript`

Cycle `20260601T203349-confirm-023687eb694076df` — 2026-06-01T20:33:49Z

PR_AUC held across 3 seeds (orig 0.9994)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `023687eb694076df` | `7262a52dd9debb84` | `7262a52dd9debb84` | `7262a52dd9debb84` |
| PR AUC | 0.9994 | 0.9993 | 0.9992 | 0.9993 |
| ROC AUC | 0.9990 | 0.9990 | 0.9990 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=023687eb694076df
```
