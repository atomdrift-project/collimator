# Confirm FAIL — 00111c37b8c7915c on `filetypes/text`

Cycle `20260608T112608-confirm-00111c37b8c7915c` — 2026-06-08T11:26:08Z

averaged ensemble PR_AUC regressed: 0.9365 -> 0.9242 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `00111c37b8c7915c` | `51f2f6651aa2e449` | `51f2f6651aa2e449` | `51f2f6651aa2e449` |
| PR AUC | 0.9365 | 0.9102 | 0.9096 | 0.9382 |
| ROC AUC | 0.9667 | 0.9646 | 0.9597 | 0.9737 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | PASS |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
