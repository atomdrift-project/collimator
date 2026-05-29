# Confirm PASS — ead9486d76066cdb on `filetypes/zst`

Cycle `20260526T191016-confirm-ead9486d76066cdb` — 2026-05-26T19:10:16Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ead9486d76066cdb` | `4c9f427e4ba79148` | `4c9f427e4ba79148` | `4c9f427e4ba79148` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ead9486d76066cdb
```
