# Confirm PASS — 2bb4b063701f7ea6 on `filetypes/shell`

Cycle `20260601T145257-confirm-2bb4b063701f7ea6` — 2026-06-01T14:52:57Z

PR_AUC held across 3 seeds (orig 0.9968)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2bb4b063701f7ea6` | `f01e0998276bdcb5` | `f01e0998276bdcb5` | `f01e0998276bdcb5` |
| PR AUC | 0.9968 | 0.9989 | 0.9987 | 0.9988 |
| ROC AUC | 0.9980 | 0.9990 | 0.9988 | 0.9989 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2bb4b063701f7ea6
```
