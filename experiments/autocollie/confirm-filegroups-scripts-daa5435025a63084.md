# Confirm PASS — daa5435025a63084 on `filegroups/scripts`

Cycle `20260715T210401-confirm-daa5435025a63084` — 2026-07-15T21:04:01Z

PR_AUC held across 3 seeds (orig 0.9938)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `daa5435025a63084` | `e538d5a20fc43653` | `e538d5a20fc43653` | `e538d5a20fc43653` |
| PR AUC | 0.9938 | 0.9949 | 0.9948 | 0.9949 |
| ROC AUC | 0.9923 | 0.9960 | 0.9959 | 0.9960 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=daa5435025a63084
```
