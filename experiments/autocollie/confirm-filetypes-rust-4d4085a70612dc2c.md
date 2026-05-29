# Confirm PASS — 4d4085a70612dc2c on `filetypes/rust`

Cycle `20260527T051053-confirm-4d4085a70612dc2c` — 2026-05-27T05:10:53Z

PR_AUC held across 3 seeds (orig 0.8786)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4d4085a70612dc2c` | `77ec220eb9848404` | `77ec220eb9848404` | `77ec220eb9848404` |
| PR AUC | 0.8786 | 0.9211 | 0.8270 | 0.9410 |
| ROC AUC | 0.9826 | 0.9902 | 0.9818 | 0.9902 |
| Recall@3FPM | — | 0.4615 | 0.1538 | 0.7692 |
| verdict | — | PASS | FAIL | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4d4085a70612dc2c
```
