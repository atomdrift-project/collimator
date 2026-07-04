# Confirm FAIL — a9076c698dfeff8c on `filetypes/pkg-info`

Cycle `20260704T135008-confirm-a9076c698dfeff8c` — 2026-07-04T13:50:08Z

averaged ensemble PR_AUC regressed: 0.9957 -> 0.9905 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a9076c698dfeff8c` | `f5965641a21149b2` | `f5965641a21149b2` | `f5965641a21149b2` |
| PR AUC | 0.9957 | 0.9904 | 0.9907 | 0.9889 |
| ROC AUC | 0.9930 | 0.9866 | 0.9835 | 0.9846 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
