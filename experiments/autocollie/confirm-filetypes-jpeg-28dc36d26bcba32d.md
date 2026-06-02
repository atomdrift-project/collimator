# Confirm PASS — 28dc36d26bcba32d on `filetypes/jpeg`

Cycle `20260602T023156-confirm-28dc36d26bcba32d` — 2026-06-02T02:31:56Z

PR_AUC held across 3 seeds (orig 0.9697)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `28dc36d26bcba32d` | `192d201966a81720` | `192d201966a81720` | `192d201966a81720` |
| PR AUC | 0.9697 | 0.9838 | 0.9828 | 0.9825 |
| ROC AUC | 0.9840 | 0.9914 | 0.9910 | 0.9902 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=28dc36d26bcba32d
```
