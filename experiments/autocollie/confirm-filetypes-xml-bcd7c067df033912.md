# Confirm PASS — bcd7c067df033912 on `filetypes/xml`

Cycle `20260525T195942-confirm-bcd7c067df033912` — 2026-05-25T19:59:42Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bcd7c067df033912` | `4a19b793967cb797` | `4a19b793967cb797` | `4a19b793967cb797` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bcd7c067df033912
```
