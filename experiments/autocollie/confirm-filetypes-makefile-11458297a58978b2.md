# Confirm PASS — 11458297a58978b2 on `filetypes/makefile`

Cycle `20260606T180902-confirm-11458297a58978b2` — 2026-06-06T18:09:02Z

PR_AUC held across 3 seeds (orig 0.0769)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `11458297a58978b2` | `d41e1a3aa531c55e` | `d41e1a3aa531c55e` | `d41e1a3aa531c55e` |
| PR AUC | 0.0769 | 0.4583 | 0.4519 | 0.4519 |
| ROC AUC | 0.5000 | 0.9062 | 0.9062 | 0.9062 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=11458297a58978b2
```
