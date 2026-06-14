# Confirm PASS — 4b58974fdcfa2857 on `filetypes/go`

Cycle `20260613T200509-confirm-4b58974fdcfa2857` — 2026-06-13T20:05:09Z

PR_AUC held across 3 seeds (orig 0.9244)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4b58974fdcfa2857` | `ade17936f884ed8f` | `ade17936f884ed8f` | `ade17936f884ed8f` |
| PR AUC | 0.9244 | 0.9210 | 0.9181 | 0.9177 |
| ROC AUC | 0.9773 | 0.9766 | 0.9762 | 0.9737 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | FAIL | FAIL |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=4b58974fdcfa2857
```
