# Confirm PASS — ffc743b50c748bf0 on `filetypes/powershell`

Cycle `20260606T151304-confirm-ffc743b50c748bf0` — 2026-06-06T15:13:04Z

PR_AUC held across 3 seeds (orig 0.9956)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ffc743b50c748bf0` | `b10f47550c4e94f4` | `b10f47550c4e94f4` | `b10f47550c4e94f4` |
| PR AUC | 0.9956 | 0.9950 | 0.9950 | 0.9939 |
| ROC AUC | 0.9897 | 0.9882 | 0.9883 | 0.9864 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ffc743b50c748bf0
```
