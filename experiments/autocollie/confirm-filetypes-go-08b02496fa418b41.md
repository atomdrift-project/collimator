# Confirm PASS — 08b02496fa418b41 on `filetypes/go`

Cycle `20260526T081217-confirm-08b02496fa418b41` — 2026-05-26T08:12:17Z

PR_AUC held across 3 seeds (orig 0.9596)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `08b02496fa418b41` | `048607c308ee38eb` | `048607c308ee38eb` | `048607c308ee38eb` |
| PR AUC | 0.9596 | 0.9735 | 0.9694 | 0.9725 |
| ROC AUC | 0.9869 | 0.9911 | 0.9901 | 0.9909 |
| Recall@3FPM | — | 0.6325 | 0.5361 | 0.5663 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=08b02496fa418b41
```
