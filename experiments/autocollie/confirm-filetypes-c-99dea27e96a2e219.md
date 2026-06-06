# Confirm PASS — 99dea27e96a2e219 on `filetypes/c`

Cycle `20260606T140254-confirm-99dea27e96a2e219` — 2026-06-06T14:02:54Z

PR_AUC held across 3 seeds (orig 0.9888)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `99dea27e96a2e219` | `39b8f3f53b882790` | `39b8f3f53b882790` | `39b8f3f53b882790` |
| PR AUC | 0.9888 | 0.9886 | 0.9890 | 0.9883 |
| ROC AUC | 0.9954 | 0.9951 | 0.9952 | 0.9946 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=99dea27e96a2e219
```
