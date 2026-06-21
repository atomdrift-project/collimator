# Confirm PASS — c48b5d7ee0d7a742 on `filetypes/go`

Cycle `20260618T021537-confirm-c48b5d7ee0d7a742` — 2026-06-18T02:15:37Z

PR_AUC held across 3 seeds (orig 0.9247)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c48b5d7ee0d7a742` | `5a9ed107e738da2c` | `5a9ed107e738da2c` | `5a9ed107e738da2c` |
| PR AUC | 0.9247 | 0.9335 | 0.9285 | 0.9302 |
| ROC AUC | 0.9763 | 0.9789 | 0.9778 | 0.9788 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=c48b5d7ee0d7a742
```
