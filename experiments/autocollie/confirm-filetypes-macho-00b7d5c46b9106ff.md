# Confirm PASS — 00b7d5c46b9106ff on `filetypes/macho`

Cycle `20260601T212619-confirm-00b7d5c46b9106ff` — 2026-06-01T21:26:19Z

PR_AUC held across 3 seeds (orig 0.9995)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `00b7d5c46b9106ff` | `f54bb0c5d8961d2c` | `f54bb0c5d8961d2c` | `f54bb0c5d8961d2c` |
| PR AUC | 0.9995 | 0.9961 | 0.9961 | 0.9967 |
| ROC AUC | 0.9999 | 0.9990 | 0.9990 | 0.9992 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=00b7d5c46b9106ff
```
