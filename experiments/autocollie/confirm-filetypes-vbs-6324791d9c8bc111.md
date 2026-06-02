# Confirm PASS — 6324791d9c8bc111 on `filetypes/vbs`

Cycle `20260602T010359-confirm-6324791d9c8bc111` — 2026-06-02T01:03:59Z

PR_AUC held across 3 seeds (orig 0.9993)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6324791d9c8bc111` | `065458b759d55656` | `065458b759d55656` | `065458b759d55656` |
| PR AUC | 0.9993 | 0.9975 | 0.9972 | 0.9970 |
| ROC AUC | 0.9989 | 0.9624 | 0.9591 | 0.9555 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=6324791d9c8bc111
```
