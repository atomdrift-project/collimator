# Confirm PASS — cdff64dcb756e96c on `filetypes/javascript`

Cycle `20260526T071223-confirm-cdff64dcb756e96c` — 2026-05-26T07:12:23Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cdff64dcb756e96c` | `adb0f9bbb971863d` | `adb0f9bbb971863d` | `adb0f9bbb971863d` |
| PR AUC | 0.9993 | 0.9996 | 0.9996 | 0.9996 |
| ROC AUC | 0.9988 | 0.9994 | 0.9994 | 0.9994 |
| Recall@3FPM | — | 0.8894 | 0.8779 | 0.8790 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=cdff64dcb756e96c
```
