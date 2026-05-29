# Confirm PASS — faffc19d41b4359d on `filetypes/applescript`

Cycle `20260527T065355-confirm-faffc19d41b4359d` — 2026-05-27T06:53:55Z

PR_AUC held across 3 seeds (orig 0.4000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `faffc19d41b4359d` | `56b250eb2216c8cb` | `56b250eb2216c8cb` | `56b250eb2216c8cb` |
| PR AUC | 0.4000 | 0.4000 | 0.4000 | 0.4000 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=faffc19d41b4359d
```
