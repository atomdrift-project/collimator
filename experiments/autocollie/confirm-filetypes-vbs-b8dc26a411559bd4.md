# Confirm PASS — b8dc26a411559bd4 on `filetypes/vbs`

Cycle `20260608T074801-confirm-b8dc26a411559bd4` — 2026-06-08T07:48:01Z

PR_AUC held across 3 seeds (orig 0.9975)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b8dc26a411559bd4` | `67141d1506a00716` | `67141d1506a00716` | `67141d1506a00716` |
| PR AUC | 0.9975 | 0.9976 | 0.9974 | 0.9974 |
| ROC AUC | 0.9914 | 0.9919 | 0.9912 | 0.9914 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b8dc26a411559bd4
```
