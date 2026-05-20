# Confirm PASS — b5ad85abb46897d5 on `filetypes/xml`

Cycle `20260519T205457-confirm-b5ad85abb46897d5` — 2026-05-19T20:54:57Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b5ad85abb46897d5` | `0871be1e08c02f05` | `0871be1e08c02f05` | `0871be1e08c02f05` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 0.9988 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 0.9998 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 0.9643 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b5ad85abb46897d5
```
