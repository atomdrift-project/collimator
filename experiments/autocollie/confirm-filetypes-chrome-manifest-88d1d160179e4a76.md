# Confirm FAIL — 88d1d160179e4a76 on `filetypes/chrome-manifest`

Cycle `20260527T050657-confirm-88d1d160179e4a76` — 2026-05-27T05:06:57Z

averaged ensemble PR_AUC regressed: 0.8444 -> 0.8000 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `88d1d160179e4a76` | `a97f9cea17600f1a` | `a97f9cea17600f1a` | `a97f9cea17600f1a` |
| PR AUC | 0.8444 | 0.5885 | 0.8833 | 0.5703 |
| ROC AUC | 0.9692 | 0.8744 | 0.9641 | 0.9359 |
| Recall@3FPM | — | 0.0000 | 0.8000 | 0.0000 |
| verdict | — | FAIL | PASS | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
