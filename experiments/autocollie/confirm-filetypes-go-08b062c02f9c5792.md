# Confirm FAIL — 08b062c02f9c5792 on `filetypes/go`

Cycle `20260821T133637-confirm-08b062c02f9c5792` — 2026-08-21T13:36:37Z

averaged ensemble PR_AUC regressed: 0.5013 -> 0.3794 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `08b062c02f9c5792` | `54767e27e20a0903` | `54767e27e20a0903` | `54767e27e20a0903` |
| PR AUC | 0.5013 | 0.3742 | 0.3673 | 0.3700 |
| ROC AUC | 0.7681 | 0.7830 | 0.7747 | 0.7653 |
| Recall@L50 | — | 0.1499 | 0.1460 | 0.1612 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
