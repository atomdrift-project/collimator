# Confirm PASS — 9a252530d540b599 on `filetypes/package.json`

Cycle `20260628T164243-confirm-9a252530d540b599` — 2026-06-28T16:42:43Z

PR_AUC held across 3 seeds (orig 0.9983)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9a252530d540b599` | `cdb1d792c3693b96` | `cdb1d792c3693b96` | `cdb1d792c3693b96` |
| PR AUC | 0.9983 | 0.9982 | 0.9982 | 0.9985 |
| ROC AUC | 0.9983 | 0.9981 | 0.9982 | 0.9985 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9a252530d540b599
```
