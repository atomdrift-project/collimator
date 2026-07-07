# Confirm PASS — fff869d779a51168 on `filetypes/ole`

Cycle `20260705T180825-confirm-fff869d779a51168` — 2026-07-05T18:08:25Z

PR_AUC held across 3 seeds (orig 0.9970)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fff869d779a51168` | `17e6cfb503603842` | `17e6cfb503603842` | `17e6cfb503603842` |
| PR AUC | 0.9970 | 0.9973 | 0.9973 | 0.9973 |
| ROC AUC | 0.9916 | 0.9914 | 0.9914 | 0.9913 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=fff869d779a51168
```
