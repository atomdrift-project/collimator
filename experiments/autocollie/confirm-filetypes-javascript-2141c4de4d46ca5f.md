# Confirm PASS — 2141c4de4d46ca5f on `filetypes/javascript`

Cycle `20260601T192527-confirm-2141c4de4d46ca5f` — 2026-06-01T19:25:27Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2141c4de4d46ca5f` | `adc6919b220e373f` | `adc6919b220e373f` | `adc6919b220e373f` |
| PR AUC | 0.9993 | 0.9992 | 0.9993 | 0.9992 |
| ROC AUC | 0.9989 | 0.9989 | 0.9990 | 0.9989 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2141c4de4d46ca5f
```
