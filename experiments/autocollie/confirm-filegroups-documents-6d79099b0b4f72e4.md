# Confirm PASS — 6d79099b0b4f72e4 on `filegroups/documents`

Cycle `20260526T221638-confirm-6d79099b0b4f72e4` — 2026-05-26T22:16:38Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6d79099b0b4f72e4` | `15c365716b800a1b` | `15c365716b800a1b` | `15c365716b800a1b` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9990 | 0.9996 | 0.9997 | 0.9997 |
| Recall@3FPM | — | 0.9736 | 0.9700 | 0.9816 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6d79099b0b4f72e4
```
