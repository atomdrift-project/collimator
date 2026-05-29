# Confirm PASS — 4e962437a9bb1e36 on `filetypes/data`

Cycle `20260526T211316-confirm-4e962437a9bb1e36` — 2026-05-26T21:13:16Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4e962437a9bb1e36` | `cbe41da239a25fdd` | `cbe41da239a25fdd` | `cbe41da239a25fdd` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4e962437a9bb1e36
```
