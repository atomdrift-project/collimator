# Confirm PASS — ecc504a347513000 on `filetypes/csharp`

Cycle `20260608T102207-confirm-ecc504a347513000` — 2026-06-08T10:22:07Z

PR_AUC held across 3 seeds (orig 0.9903)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ecc504a347513000` | `9c2f2398f585c87c` | `9c2f2398f585c87c` | `9c2f2398f585c87c` |
| PR AUC | 0.9903 | 0.9896 | 0.9878 | 0.9886 |
| ROC AUC | 0.9933 | 0.9937 | 0.9921 | 0.9913 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=ecc504a347513000
```
