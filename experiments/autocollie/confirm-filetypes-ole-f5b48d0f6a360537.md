# Confirm PASS — f5b48d0f6a360537 on `filetypes/ole`

Cycle `20260609T100435-confirm-f5b48d0f6a360537` — 2026-06-09T10:04:35Z

PR_AUC held across 3 seeds (orig 0.9948)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f5b48d0f6a360537` | `24a876081c33c29a` | `24a876081c33c29a` | `24a876081c33c29a` |
| PR AUC | 0.9948 | 0.9948 | 0.9946 | 0.9945 |
| ROC AUC | 0.9937 | 0.9936 | 0.9934 | 0.9932 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=f5b48d0f6a360537
```
