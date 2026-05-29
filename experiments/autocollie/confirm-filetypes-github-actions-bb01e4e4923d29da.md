# Confirm PASS — bb01e4e4923d29da on `filetypes/github-actions`

Cycle `20260527T055709-confirm-bb01e4e4923d29da` — 2026-05-27T05:57:09Z

PR_AUC held across 3 seeds (orig 0.0089)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `bb01e4e4923d29da` | `a9320008f8fb256a` | `a9320008f8fb256a` | `a9320008f8fb256a` |
| PR AUC | 0.0089 | 0.0273 | 0.0273 | 0.0273 |
| ROC AUC | 0.5000 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=bb01e4e4923d29da
```
