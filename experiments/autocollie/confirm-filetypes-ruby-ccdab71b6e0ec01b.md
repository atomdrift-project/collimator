# Confirm FAIL — ccdab71b6e0ec01b on `filetypes/ruby`

Cycle `20260526T191521-confirm-ccdab71b6e0ec01b` — 2026-05-26T19:15:21Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9134 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ccdab71b6e0ec01b` | `1e7bc78eb4c453a0` | `1e7bc78eb4c453a0` | `1e7bc78eb4c453a0` |
| PR AUC | 1.0000 | 0.8497 | 0.9237 | 0.8908 |
| ROC AUC | 1.0000 | 0.9949 | 0.9968 | 0.9949 |
| Recall@3FPM | — | 0.2222 | 0.5556 | 0.4444 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
