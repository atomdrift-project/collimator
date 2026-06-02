# Confirm FAIL — 3639896e9723ddf0 on `filetypes/rust`

Cycle `20260602T014249-confirm-3639896e9723ddf0` — 2026-06-02T01:42:49Z

averaged ensemble PR_AUC regressed: 0.9101 -> 0.9032 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3639896e9723ddf0` | `970976c1dd687814` | `970976c1dd687814` | `970976c1dd687814` |
| PR AUC | 0.9101 | 0.9015 | 0.9007 | 0.9243 |
| ROC AUC | 0.9898 | 0.9890 | 0.9890 | 0.9922 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | PASS |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
