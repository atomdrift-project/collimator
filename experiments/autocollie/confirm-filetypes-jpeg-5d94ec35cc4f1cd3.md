# Confirm FAIL — 5d94ec35cc4f1cd3 on `filetypes/jpeg`

Cycle `20260525T211541-confirm-5d94ec35cc4f1cd3` — 2026-05-25T21:15:41Z

averaged ensemble PR_AUC regressed: 0.9805 -> 0.9707 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5d94ec35cc4f1cd3` | `00d49ef1b15e62fe` | `00d49ef1b15e62fe` | `00d49ef1b15e62fe` |
| PR AUC | 0.9805 | 0.9767 | 0.9697 | 0.9712 |
| ROC AUC | 0.9851 | 0.9806 | 0.9771 | 0.9771 |
| Recall@3FPM | — | 0.8000 | 0.6400 | 0.7200 |
| verdict | — | PASS | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
