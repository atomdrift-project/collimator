# Confirm PASS — 0a1ebe557a204709 on `filetypes/python`

Cycle `20260525T210330-confirm-0a1ebe557a204709` — 2026-05-25T21:03:30Z

PR_AUC held across 3 seeds (orig 0.9992)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0a1ebe557a204709` | `06c5a191687e54a3` | `06c5a191687e54a3` | `06c5a191687e54a3` |
| PR AUC | 0.9992 | 0.9986 | 0.9983 | 0.9985 |
| ROC AUC | 0.9992 | 0.9988 | 0.9985 | 0.9987 |
| Recall@3FPM | — | 0.8340 | 0.7395 | 0.8249 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0a1ebe557a204709
```
