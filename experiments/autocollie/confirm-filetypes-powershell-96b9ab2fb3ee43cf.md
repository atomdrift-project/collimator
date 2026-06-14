# Confirm PASS — 96b9ab2fb3ee43cf on `filetypes/powershell`

Cycle `20260614T213202-confirm-96b9ab2fb3ee43cf` — 2026-06-14T21:32:02Z

PR_AUC held across 3 seeds (orig 0.9934)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `96b9ab2fb3ee43cf` | `815ed80ba3f32371` | `815ed80ba3f32371` | `815ed80ba3f32371` |
| PR AUC | 0.9934 | 0.9933 | 0.9929 | 0.9927 |
| ROC AUC | 0.9838 | 0.9834 | 0.9826 | 0.9819 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=96b9ab2fb3ee43cf
```
