# Confirm PASS — ed58b8f67b18373d on `filetypes/zip`

Cycle `20260609T103806-confirm-ed58b8f67b18373d` — 2026-06-09T10:38:06Z

PR_AUC held across 3 seeds (orig 0.9996)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ed58b8f67b18373d` | `ffe797bc65bce2c9` | `ffe797bc65bce2c9` | `ffe797bc65bce2c9` |
| PR AUC | 0.9996 | 0.9995 | 0.9996 | 0.9996 |
| ROC AUC | 0.9960 | 0.9961 | 0.9961 | 0.9966 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ed58b8f67b18373d
```
