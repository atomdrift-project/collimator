# Confirm PASS — 3c68ae673b1511cb on `filetypes/docx`

Cycle `20260526T212156-confirm-3c68ae673b1511cb` — 2026-05-26T21:21:56Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3c68ae673b1511cb` | `e7d40b2f18aa1072` | `e7d40b2f18aa1072` | `e7d40b2f18aa1072` |
| PR AUC | 1.0000 | 0.9992 | 0.9985 | 0.9995 |
| ROC AUC | 1.0000 | 0.9937 | 0.9893 | 0.9962 |
| Recall@3FPM | — | 0.9602 | 0.7920 | 0.9336 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=3c68ae673b1511cb
```
