# Confirm PASS — dafcdaa2b889beda on `filegroups/documents`

Cycle `20260616T085209-confirm-dafcdaa2b889beda` — 2026-06-16T08:52:09Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `dafcdaa2b889beda` | `54ae88ce204ffb76` | `54ae88ce204ffb76` | `54ae88ce204ffb76` |
| PR AUC | 0.9999 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9989 | 0.9992 | 0.9992 | 0.9991 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=dafcdaa2b889beda
```
