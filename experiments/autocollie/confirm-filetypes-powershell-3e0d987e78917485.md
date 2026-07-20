# Confirm PASS — 3e0d987e78917485 on `filetypes/powershell`

Cycle `20260711T110951-confirm-3e0d987e78917485` — 2026-07-11T11:09:51Z

PR_AUC held across 3 seeds (orig 0.9987)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3e0d987e78917485` | `ce0edc54a83892a7` | `ce0edc54a83892a7` | `ce0edc54a83892a7` |
| PR AUC | 0.9987 | 0.9988 | 0.9988 | 0.9986 |
| ROC AUC | 0.9953 | 0.9958 | 0.9956 | 0.9951 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3e0d987e78917485
```
