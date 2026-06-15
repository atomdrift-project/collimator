# Confirm PASS — bf97bdeec463191a on `filetypes/pe`

Cycle `20260615T002409-confirm-bf97bdeec463191a` — 2026-06-15T00:24:09Z

PR_AUC held across 3 seeds (orig 0.9988)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bf97bdeec463191a` | `cda7fe2b4adbf2cd` | `cda7fe2b4adbf2cd` | `cda7fe2b4adbf2cd` |
| PR AUC | 0.9988 | 1.0000 | 1.0000 | 0.9999 |
| ROC AUC | 0.9988 | 0.9996 | 0.9996 | 0.9996 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bf97bdeec463191a
```
