# Confirm PASS — 95897481f565eef2 on `filetypes/xml`

Cycle `20260520T081749-confirm-95897481f565eef2` — 2026-05-20T08:17:49Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `95897481f565eef2` | `1613538c79043b94` | `1613538c79043b94` | `1613538c79043b94` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=95897481f565eef2
```
