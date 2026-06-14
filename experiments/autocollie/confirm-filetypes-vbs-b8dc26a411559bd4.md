# Confirm PASS — b8dc26a411559bd4 on `filetypes/vbs`

Cycle `20260614T044944-confirm-b8dc26a411559bd4` — 2026-06-14T04:49:44Z

PR_AUC held across 3 seeds (orig 0.9975)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b8dc26a411559bd4` | `e88f560d9b2008a6` | `e88f560d9b2008a6` | `e88f560d9b2008a6` |
| PR AUC | 0.9975 | 0.9966 | 0.9968 | 0.9971 |
| ROC AUC | 0.9914 | 0.9872 | 0.9885 | 0.9893 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b8dc26a411559bd4
```
