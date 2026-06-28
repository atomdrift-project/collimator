# Confirm FAIL — 48f9c3c074f6c798 on `filetypes/java_class`

Cycle `20260628T121132-confirm-48f9c3c074f6c798` — 2026-06-28T12:11:32Z

averaged ensemble PR_AUC regressed: 0.8921 -> 0.8091 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `48f9c3c074f6c798` | `6ab5561d8b8a200d` | `6ab5561d8b8a200d` | `6ab5561d8b8a200d` |
| PR AUC | 0.8921 | 0.1595 | 0.8091 | 0.1595 |
| ROC AUC | 0.9548 | 0.8936 | 0.8688 | 0.8936 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
