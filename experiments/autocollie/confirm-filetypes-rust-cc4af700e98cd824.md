# Confirm FAIL — cc4af700e98cd824 on `filetypes/rust`

Cycle `20260606T180617-confirm-cc4af700e98cd824` — 2026-06-06T18:06:17Z

averaged ensemble PR_AUC regressed: 0.0992 -> 0.0871 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `cc4af700e98cd824` | `b95217c7070676c5` | `b95217c7070676c5` | `b95217c7070676c5` |
| PR AUC | 0.0992 | 0.0795 | 0.0749 | 0.0708 |
| ROC AUC | 0.5524 | 0.4503 | 0.4513 | 0.4633 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
