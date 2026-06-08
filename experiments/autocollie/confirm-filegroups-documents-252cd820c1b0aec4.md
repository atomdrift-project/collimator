# Confirm PASS — 252cd820c1b0aec4 on `filegroups/documents`

Cycle `20260608T114113-confirm-252cd820c1b0aec4` — 2026-06-08T11:41:13Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `252cd820c1b0aec4` | `7976de1ecad62806` | `7976de1ecad62806` | `7976de1ecad62806` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9991 | 0.9991 | 0.9992 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=252cd820c1b0aec4
```
