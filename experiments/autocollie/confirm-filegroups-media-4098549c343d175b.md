# Confirm PASS — 4098549c343d175b on `filegroups/media`

Cycle `20260608T100813-confirm-4098549c343d175b` — 2026-06-08T10:08:13Z

PR_AUC held across 3 seeds (orig 0.9651)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4098549c343d175b` | `664423dfe522aab6` | `664423dfe522aab6` | `664423dfe522aab6` |
| PR AUC | 0.9651 | 0.9728 | 0.9648 | 0.9725 |
| ROC AUC | 0.9791 | 0.9844 | 0.9813 | 0.9759 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4098549c343d175b
```
