# Confirm FAIL — 739734f5cba4b62c on `filegroups/media`

Cycle `20260703T043027-confirm-739734f5cba4b62c` — 2026-07-03T04:30:27Z

averaged ensemble PR_AUC regressed: 0.3443 -> 0.1111 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `739734f5cba4b62c` | `8fa7e2fc33ca9f65` | `8fa7e2fc33ca9f65` | `8fa7e2fc33ca9f65` |
| PR AUC | 0.3443 | 0.1243 | 0.1043 | 0.1128 |
| ROC AUC | 0.7566 | 0.5545 | 0.4128 | 0.4496 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
