# Confirm PASS — 098c90bc97ffb123 on `filetypes/package.json`

Cycle `20260606T075059-confirm-098c90bc97ffb123` — 2026-06-06T07:50:59Z

PR_AUC held across 3 seeds (orig 0.9989)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `098c90bc97ffb123` | `e6d97acb65239354` | `e6d97acb65239354` | `e6d97acb65239354` |
| PR AUC | 0.9989 | 0.9990 | 0.9990 | 0.9990 |
| ROC AUC | 0.9982 | 0.9983 | 0.9985 | 0.9984 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=098c90bc97ffb123
```
