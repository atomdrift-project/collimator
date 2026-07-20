# Confirm PASS — 92cb45c23a446ecb on `filetypes/pdf`

Cycle `20260713T052608-confirm-92cb45c23a446ecb` — 2026-07-13T05:26:08Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `92cb45c23a446ecb` | `21970c1c2a83655a` | `21970c1c2a83655a` | `21970c1c2a83655a` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 0.9995 | 0.9992 | 0.9992 | 0.9992 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=92cb45c23a446ecb
```
