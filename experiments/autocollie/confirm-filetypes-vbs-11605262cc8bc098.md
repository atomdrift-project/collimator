# Confirm PASS — 11605262cc8bc098 on `filetypes/vbs`

Cycle `20260613T232104-confirm-11605262cc8bc098` — 2026-06-13T23:21:04Z

PR_AUC held across 3 seeds (orig 0.9967)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `11605262cc8bc098` | `dc3fd010667cb045` | `dc3fd010667cb045` | `dc3fd010667cb045` |
| PR AUC | 0.9967 | 0.9973 | 0.9975 | 0.9970 |
| ROC AUC | 0.9887 | 0.9902 | 0.9910 | 0.9891 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=11605262cc8bc098
```
