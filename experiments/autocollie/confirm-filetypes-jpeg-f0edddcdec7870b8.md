# Confirm PASS — f0edddcdec7870b8 on `filetypes/jpeg`

Cycle `20260609T081313-confirm-f0edddcdec7870b8` — 2026-06-09T08:13:13Z

PR_AUC held across 3 seeds (orig 0.9530)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f0edddcdec7870b8` | `d0c5a52c4c509b68` | `d0c5a52c4c509b68` | `d0c5a52c4c509b68` |
| PR AUC | 0.9530 | 0.9550 | 0.9574 | 0.9536 |
| ROC AUC | 0.9750 | 0.9764 | 0.9770 | 0.9772 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f0edddcdec7870b8
```
