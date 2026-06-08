# Confirm PASS — 031999071f35bb21 on `filetypes/python`

Cycle `20260608T182525-confirm-031999071f35bb21` — 2026-06-08T18:25:25Z

PR_AUC held across 3 seeds (orig 0.9990)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `031999071f35bb21` | `92817fa0b92c8d20` | `92817fa0b92c8d20` | `92817fa0b92c8d20` |
| PR AUC | 0.9990 | 0.9943 | 0.9942 | 0.9943 |
| ROC AUC | 0.9991 | 0.9954 | 0.9953 | 0.9956 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=031999071f35bb21
```
