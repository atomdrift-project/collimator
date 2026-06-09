# Confirm PASS — 2649353f84242da3 on `filetypes/xml`

Cycle `20260609T111756-confirm-2649353f84242da3` — 2026-06-09T11:17:56Z

PR_AUC held across 3 seeds (orig 0.9952)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `2649353f84242da3` | `05b51ab52ac2b543` | `05b51ab52ac2b543` | `05b51ab52ac2b543` |
| PR AUC | 0.9952 | 0.9967 | 0.9952 | 0.9966 |
| ROC AUC | 0.9984 | 0.9990 | 0.9984 | 0.9990 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=2649353f84242da3
```
