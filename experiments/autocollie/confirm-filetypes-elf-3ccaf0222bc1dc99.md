# Confirm PASS — 3ccaf0222bc1dc99 on `filetypes/elf`

Cycle `20260609T074003-confirm-3ccaf0222bc1dc99` — 2026-06-09T07:40:03Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3ccaf0222bc1dc99` | `86dba931f919159c` | `86dba931f919159c` | `86dba931f919159c` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9999 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3ccaf0222bc1dc99
```
