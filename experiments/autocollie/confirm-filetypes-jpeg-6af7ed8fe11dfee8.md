# Confirm FAIL — 6af7ed8fe11dfee8 on `filetypes/jpeg`

Cycle `20260527T010533-confirm-6af7ed8fe11dfee8` — 2026-05-27T01:05:33Z

averaged ensemble PR_AUC regressed: 0.9783 -> 0.9707 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `6af7ed8fe11dfee8` | `5a25e6fa06f3b3a3` | `5a25e6fa06f3b3a3` | `5a25e6fa06f3b3a3` |
| PR AUC | 0.9783 | 0.9817 | 0.9712 | 0.9669 |
| ROC AUC | 0.9826 | 0.9840 | 0.9783 | 0.9737 |
| Recall@3FPM | — | 0.8800 | 0.6400 | 0.7200 |
| verdict | — | PASS | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
