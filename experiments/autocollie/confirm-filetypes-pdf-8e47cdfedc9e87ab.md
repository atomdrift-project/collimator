# Confirm FAIL — 8e47cdfedc9e87ab on `filetypes/pdf`

Cycle `20260609T103805-confirm-8e47cdfedc9e87ab` — 2026-06-09T10:38:05Z

averaged ensemble PR_AUC regressed: 1.0000 -> 0.9900 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `8e47cdfedc9e87ab` | `31edf2433db0fb94` | `31edf2433db0fb94` | `31edf2433db0fb94` |
| PR AUC | 1.0000 | 0.9900 | 0.9900 | 0.9900 |
| ROC AUC | 0.9989 | 0.5000 | 0.5000 | 0.5000 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
