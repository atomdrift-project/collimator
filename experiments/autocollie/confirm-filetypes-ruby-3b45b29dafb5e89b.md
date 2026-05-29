# Confirm FAIL — 3b45b29dafb5e89b on `filetypes/ruby`

Cycle `20260525T195454-confirm-3b45b29dafb5e89b` — 2026-05-25T19:54:54Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.8649 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3b45b29dafb5e89b` | `d48b2f5d05fc2789` | `d48b2f5d05fc2789` | `d48b2f5d05fc2789` |
| PR AUC | 1.0000 | 0.8560 | 0.8949 | 0.8338 |
| ROC AUC | 1.0000 | 0.9926 | 0.9954 | 0.9931 |
| Recall@3FPM | — | 0.3333 | 0.4444 | 0.2222 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
