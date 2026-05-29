# Confirm PASS — b8f9638ffe8a8e1b on `filetypes/pptx`

Cycle `20260527T081933-confirm-b8f9638ffe8a8e1b` — 2026-05-27T08:19:33Z

PR_AUC held across 3 seeds (orig 0.9231)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `b8f9638ffe8a8e1b` | `1a6884ddb87523a8` | `1a6884ddb87523a8` | `1a6884ddb87523a8` |
| PR AUC | 0.9231 | 0.9231 | 0.9231 | 0.9231 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=b8f9638ffe8a8e1b
```
