# Confirm PASS — bbfdac417f933592 on `filetypes/objc`

Cycle `20260527T053952-confirm-bbfdac417f933592` — 2026-05-27T05:39:52Z

PR_AUC held across 3 seeds (orig 0.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bbfdac417f933592` | `b8c11404f19fc7e6` | `b8c11404f19fc7e6` | `b8c11404f19fc7e6` |
| PR AUC | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| ROC AUC | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bbfdac417f933592
```
