# Confirm PASS — 8d38ee455fc8f155 on `filetypes/go`

Cycle `20260526T075341-confirm-8d38ee455fc8f155` — 2026-05-26T07:53:41Z

PR_AUC held across 3 seeds (orig 0.9588)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8d38ee455fc8f155` | `f5c8d9f1bc9ecbae` | `f5c8d9f1bc9ecbae` | `f5c8d9f1bc9ecbae` |
| PR AUC | 0.9588 | 0.9665 | 0.9663 | 0.9674 |
| ROC AUC | 0.9858 | 0.9886 | 0.9892 | 0.9891 |
| Recall@3FPM | — | 0.5964 | 0.4819 | 0.4699 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8d38ee455fc8f155
```
