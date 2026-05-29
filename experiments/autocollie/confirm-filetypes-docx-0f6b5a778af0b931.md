# Confirm PASS — 0f6b5a778af0b931 on `filetypes/docx`

Cycle `20260527T051433-confirm-0f6b5a778af0b931` — 2026-05-27T05:14:33Z

PR_AUC held across 3 seeds (orig 0.9970)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `0f6b5a778af0b931` | `4550c9ce8caf699b` | `4550c9ce8caf699b` | `4550c9ce8caf699b` |
| PR AUC | 0.9970 | 0.9970 | 0.9979 | 0.9971 |
| ROC AUC | 0.9830 | 0.9830 | 0.9867 | 0.9835 |
| Recall@3FPM | — | 0.5133 | 0.6460 | 0.5177 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=0f6b5a778af0b931
```
