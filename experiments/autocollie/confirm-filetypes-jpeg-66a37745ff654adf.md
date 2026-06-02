# Confirm PASS — 66a37745ff654adf on `filetypes/jpeg`

Cycle `20260602T032330-confirm-66a37745ff654adf` — 2026-06-02T03:23:30Z

PR_AUC held across 3 seeds (orig 0.9407)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `66a37745ff654adf` | `0a730ef7978ae933` | `0a730ef7978ae933` | `0a730ef7978ae933` |
| PR AUC | 0.9407 | 0.9491 | 0.9504 | 0.9687 |
| ROC AUC | 0.9691 | 0.9734 | 0.9746 | 0.9824 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=66a37745ff654adf
```
