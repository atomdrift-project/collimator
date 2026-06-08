# Confirm FAIL — f2fba1536fc537d0 on `filetypes/python`

Cycle `20260608T182419-confirm-f2fba1536fc537d0` — 2026-06-08T18:24:19Z

averaged ensemble PR_AUC regressed: 0.9989 -> 0.9903 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f2fba1536fc537d0` | `7f719d1494876ec2` | `7f719d1494876ec2` | `7f719d1494876ec2` |
| PR AUC | 0.9989 | 0.9899 | 0.9903 | 0.9900 |
| ROC AUC | 0.9989 | 0.9912 | 0.9918 | 0.9915 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
