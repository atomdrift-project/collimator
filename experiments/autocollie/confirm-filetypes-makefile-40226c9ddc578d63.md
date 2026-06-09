# Confirm PASS — 40226c9ddc578d63 on `filetypes/makefile`

Cycle `20260609T002658-confirm-40226c9ddc578d63` — 2026-06-09T00:26:58Z

PR_AUC held across 3 seeds (orig 0.5122)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `40226c9ddc578d63` | `06a3deebf9a54dad` | `06a3deebf9a54dad` | `06a3deebf9a54dad` |
| PR AUC | 0.5122 | 0.6393 | 0.5676 | 0.6193 |
| ROC AUC | 0.8914 | 0.9333 | 0.9273 | 0.9273 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | PASS | PASS | PASS |

## Next step

The held-out signal reproduced under all 3 confirm seeds. To proceed to full-corpus training and policy comparison:

```
make autocollie-promote KEY=40226c9ddc578d63
```
