# Confirm PASS — ee4bb9baaaa18f7e on `filetypes/javascript`

Cycle `20260616T060844-confirm-ee4bb9baaaa18f7e` — 2026-06-16T06:08:44Z

PR_AUC held across 3 seeds (orig 0.9976)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ee4bb9baaaa18f7e` | `a1e5bd889270deec` | `a1e5bd889270deec` | `a1e5bd889270deec` |
| PR AUC | 0.9976 | 0.9991 | 0.9991 | 0.9991 |
| ROC AUC | 0.9971 | 0.9988 | 0.9987 | 0.9988 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ee4bb9baaaa18f7e
```
