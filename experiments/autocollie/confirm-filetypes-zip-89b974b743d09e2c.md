# Confirm PASS — 89b974b743d09e2c on `filetypes/zip`

Cycle `20260526T230709-confirm-89b974b743d09e2c` — 2026-05-26T23:07:09Z

PR_AUC held across 3 seeds (orig 0.9999)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `89b974b743d09e2c` | `9a58400e04407d76` | `9a58400e04407d76` | `9a58400e04407d76` |
| PR AUC | 0.9999 | 0.9998 | 0.9998 | 0.9998 |
| ROC AUC | 0.9982 | 0.9962 | 0.9962 | 0.9963 |
| Recall@3FPM | — | 0.6672 | 0.6887 | 0.7194 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=89b974b743d09e2c
```
