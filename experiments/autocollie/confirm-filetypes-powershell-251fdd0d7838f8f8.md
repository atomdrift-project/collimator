# Confirm PASS — 251fdd0d7838f8f8 on `filetypes/powershell`

Cycle `20260613T014547-confirm-251fdd0d7838f8f8` — 2026-06-13T01:45:47Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `251fdd0d7838f8f8` | `ca4dd96a61988b79` | `ca4dd96a61988b79` | `ca4dd96a61988b79` |
| PR AUC | 0.9989 | 0.9988 | 0.9989 | 0.9990 |
| ROC AUC | 0.9941 | 0.9934 | 0.9941 | 0.9945 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=251fdd0d7838f8f8
```
