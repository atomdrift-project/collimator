# Confirm PASS — 0eb378f5b044e890 on `filetypes/python`

Cycle `20260723T090130-confirm-0eb378f5b044e890` — 2026-07-23T09:01:30Z

PR_AUC held across 3 seeds (orig 0.9737)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0eb378f5b044e890` | `8c343dcfe2fbba70` | `8c343dcfe2fbba70` | `8c343dcfe2fbba70` |
| PR AUC | 0.9737 | 0.9783 | 0.9787 | 0.9785 |
| ROC AUC | 0.9884 | 0.9904 | 0.9905 | 0.9904 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0eb378f5b044e890
```
