# Confirm PASS — 9a45f40c8b0a3f45 on `filetypes/xml`

Cycle `20260526T200451-confirm-9a45f40c8b0a3f45` — 2026-05-26T20:04:51Z

PR_AUC held across 3 seeds (orig 1.0000)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9a45f40c8b0a3f45` | `4b6e4065bc202e77` | `4b6e4065bc202e77` | `4b6e4065bc202e77` |
| PR AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| Recall@3FPM | — | 1.0000 | 1.0000 | 1.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=9a45f40c8b0a3f45
```
