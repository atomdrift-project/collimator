# Confirm FAIL — fba398b4d10ce63a on `filetypes/yaml`

Cycle `20261106T013037-confirm-fba398b4d10ce63a` — 2026-11-06T01:30:37Z

averaged ensemble PR_AUC regressed: 0.2416 -> 0.2266 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `fba398b4d10ce63a` | `8eae45e1bdcff3c8` | `8eae45e1bdcff3c8` | `8eae45e1bdcff3c8` |
| PR AUC | 0.2416 | 0.2133 | 0.2538 | 0.2007 |
| ROC AUC | 0.9550 | 0.9543 | 0.9548 | 0.9519 |
| Recall@L50 | — | 0.0096 | 0.0192 | — |
| verdict | — | FAIL | PASS | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
