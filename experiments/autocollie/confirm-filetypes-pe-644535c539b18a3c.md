# Confirm PASS — 644535c539b18a3c on `filetypes/pe`

Cycle `20260609T101631-confirm-644535c539b18a3c` — 2026-06-09T10:16:31Z

PR_AUC held across 3 seeds (orig 0.9991)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `644535c539b18a3c` | `95547008e7c79faf` | `95547008e7c79faf` | `95547008e7c79faf` |
| PR AUC | 0.9991 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9992 | 0.9998 | 0.9998 | 0.9997 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=644535c539b18a3c
```
