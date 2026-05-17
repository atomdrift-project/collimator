# Confirm PASS — daed09dabb05d097 on `filetypes/elf`

Cycle `20260514T184253-confirm-daed09dabb05d097` — 2026-05-14T18:42:53Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `daed09dabb05d097` | `b84e525b3054c53b` | `b84e525b3054c53b` | `b84e525b3054c53b` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 0.9607 | 0.9635 | 0.9689 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=daed09dabb05d097
```
