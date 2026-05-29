# Confirm PASS — eddae231a0edca42 on `filetypes/elf`

Cycle `20260526T162425-confirm-eddae231a0edca42` — 2026-05-26T16:24:25Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `eddae231a0edca42` | `2a71f1a5e30a64c6` | `2a71f1a5e30a64c6` | `2a71f1a5e30a64c6` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 0.9841 | 0.9757 | 0.9833 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=eddae231a0edca42
```
