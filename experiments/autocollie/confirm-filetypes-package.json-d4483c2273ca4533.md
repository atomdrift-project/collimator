# Confirm PASS — d4483c2273ca4533 on `filetypes/package.json`

Cycle `20260625T200113-confirm-d4483c2273ca4533` — 2026-06-25T20:01:13Z

PR_AUC held across 3 seeds (orig 0.9991)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `d4483c2273ca4533` | `1e966f4c57e82cc9` | `1e966f4c57e82cc9` | `1e966f4c57e82cc9` |
| PR AUC | 0.9991 | 0.9990 | 0.9992 | 0.9992 |
| ROC AUC | 0.9988 | 0.9987 | 0.9990 | 0.9989 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=d4483c2273ca4533
```
