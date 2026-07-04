# Confirm FAIL — 79d3235f3626e1e9 on `filegroups/source`

Cycle `20260704T154307-confirm-79d3235f3626e1e9` — 2026-07-04T15:43:07Z

averaged ensemble PR_AUC regressed: 0.8672 -> 0.4638 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `79d3235f3626e1e9` | `d798045f3f018ea9` | `d798045f3f018ea9` | `d798045f3f018ea9` |
| PR AUC | 0.8672 | 0.4574 | 0.4655 | 0.4625 |
| ROC AUC | 0.8472 | 0.8283 | 0.8504 | 0.8344 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
