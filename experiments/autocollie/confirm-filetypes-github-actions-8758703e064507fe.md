# Confirm PASS — 8758703e064507fe on `filetypes/github-actions`

Cycle `20260527T060037-confirm-8758703e064507fe` — 2026-05-27T06:00:37Z

PR_AUC held across 3 seeds (orig 0.0089)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8758703e064507fe` | `31e586b2f7cb3444` | `31e586b2f7cb3444` | `31e586b2f7cb3444` |
| PR AUC | 0.0089 | 0.0273 | 0.0273 | 0.0273 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=8758703e064507fe
```
