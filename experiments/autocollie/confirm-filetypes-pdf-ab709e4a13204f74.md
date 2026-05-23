# Confirm FAIL — ab709e4a13204f74 on `filetypes/pdf`

Cycle `20260523T194200-confirm-ab709e4a13204f74` — 2026-05-23T19:42:00Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9942 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ab709e4a13204f74` | `f92c61b6563d05d2` | `f92c61b6563d05d2` | `f92c61b6563d05d2` |
| PR AUC | 1.0000 | 0.9942 | 0.9942 | 0.9942 |
| ROC AUC | 0.9991 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
