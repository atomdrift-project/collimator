# Confirm PASS — 022de0feb3411ead on `filegroups/media`

Cycle `20260525T211102-confirm-022de0feb3411ead` — 2026-05-25T21:11:02Z

PR_AUC held across 3 seeds (orig 0.9985)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `022de0feb3411ead` | `2d68c0eefa968ce7` | `2d68c0eefa968ce7` | `2d68c0eefa968ce7` |
| PR AUC | 0.9985 | 0.9985 | 0.9981 | 0.9989 |
| ROC AUC | 0.9982 | 0.9983 | 0.9978 | 0.9987 |
| Recall@3FPM | — | 0.9444 | 0.8889 | 0.9667 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=022de0feb3411ead
```
