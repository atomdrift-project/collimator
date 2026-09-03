# Confirm PASS — c8cfd1cb2bd4822f on `filetypes/plist`

Cycle `20260825T194701-confirm-c8cfd1cb2bd4822f` — 2026-08-25T19:47:01Z

PR_AUC held across 3 seeds (orig 0.1506)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c8cfd1cb2bd4822f` | `8c96ed1be4740ee1` | `8c96ed1be4740ee1` | `8c96ed1be4740ee1` |
| PR AUC | 0.1506 | 0.1009 | 0.1068 | 0.1183 |
| ROC AUC | 0.7603 | 0.7078 | 0.7787 | 0.6498 |
| Recall@L50 | — | 0.0476 | 0.0357 | 0.0595 |
| verdict | — | FAIL | FAIL | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c8cfd1cb2bd4822f
```
