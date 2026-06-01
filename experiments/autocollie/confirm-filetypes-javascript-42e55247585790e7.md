# Confirm PASS — 42e55247585790e7 on `filetypes/javascript`

Cycle `20260601T204247-confirm-42e55247585790e7` — 2026-06-01T20:42:47Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `42e55247585790e7` | `58ff2570e06b272e` | `58ff2570e06b272e` | `58ff2570e06b272e` |
| PR AUC | 0.9988 | 0.9993 | 0.9993 | 0.9993 |
| ROC AUC | 0.9984 | 0.9990 | 0.9991 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=42e55247585790e7
```
