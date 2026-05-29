# Confirm PASS — e9bcc44a002ca91f on `filetypes/gz`

Cycle `20260526T205249-confirm-e9bcc44a002ca91f` — 2026-05-26T20:52:49Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e9bcc44a002ca91f` | `f9a7cb9485105faa` | `f9a7cb9485105faa` | `f9a7cb9485105faa` |
| PR AUC | 1.0000 | 0.9981 | 0.9985 | 0.9985 |
| ROC AUC | 1.0000 | 0.9975 | 0.9980 | 0.9980 |
| Recall@3FPM | — | 0.9826 | 0.9913 | 0.9913 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=e9bcc44a002ca91f
```
