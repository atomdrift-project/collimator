# Confirm PASS — 68fae179959c68c4 on `filetypes/python`

Cycle `20260601T214549-confirm-68fae179959c68c4` — 2026-06-01T21:45:49Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `68fae179959c68c4` | `664f16a3a4c95074` | `664f16a3a4c95074` | `664f16a3a4c95074` |
| PR AUC | 0.9990 | 0.9974 | 0.9974 | 0.9972 |
| ROC AUC | 0.9991 | 0.9981 | 0.9981 | 0.9980 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=68fae179959c68c4
```
