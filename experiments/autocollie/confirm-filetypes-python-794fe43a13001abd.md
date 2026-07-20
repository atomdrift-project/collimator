# Confirm PASS — 794fe43a13001abd on `filetypes/python`

Cycle `20260715T231208-confirm-794fe43a13001abd` — 2026-07-15T23:12:08Z

PR_AUC held across 3 seeds (orig 0.9739)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `794fe43a13001abd` | `190b098dee691822` | `190b098dee691822` | `190b098dee691822` |
| PR AUC | 0.9739 | 0.9782 | 0.9779 | 0.9787 |
| ROC AUC | 0.9876 | 0.9896 | 0.9892 | 0.9900 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=794fe43a13001abd
```
