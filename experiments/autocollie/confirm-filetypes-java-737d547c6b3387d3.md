# Confirm FAIL — 737d547c6b3387d3 on `filetypes/java`

Cycle `20260527T053535-confirm-737d547c6b3387d3` — 2026-05-27T05:35:35Z

averaged ensemble PR_AUC regressed: 0.5667 -> 0.5159 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `737d547c6b3387d3` | `7a6595cd3fe217ad` | `7a6595cd3fe217ad` | `7a6595cd3fe217ad` |
| PR AUC | 0.5667 | 0.4881 | 0.5214 | 0.5714 |
| ROC AUC | 0.8542 | 0.8229 | 0.8542 | 0.8646 |
| Recall@3FPM | — | 0.3333 | 0.3333 | 0.3333 |
| verdict | — | FAIL | FAIL | PASS |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
