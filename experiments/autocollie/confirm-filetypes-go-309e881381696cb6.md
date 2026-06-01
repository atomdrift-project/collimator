# Confirm PASS — 309e881381696cb6 on `filetypes/go`

Cycle `20260601T153931-confirm-309e881381696cb6` — 2026-06-01T15:39:31Z

PR_AUC held across 3 seeds (orig 0.9625)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `309e881381696cb6` | `af41bcc881482014` | `af41bcc881482014` | `af41bcc881482014` |
| PR AUC | 0.9625 | 0.9652 | 0.9577 | 0.9598 |
| ROC AUC | 0.9858 | 0.9902 | 0.9871 | 0.9884 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=309e881381696cb6
```
