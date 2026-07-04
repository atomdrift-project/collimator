# Confirm FAIL — 5bc8789d2cf86137 on `filegroups/config`

Cycle `20260704T135132-confirm-5bc8789d2cf86137` — 2026-07-04T13:51:32Z

averaged ensemble PR_AUC regressed: 0.9019 -> 0.8258 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `5bc8789d2cf86137` | `91ca8299fbb1e7f0` | `91ca8299fbb1e7f0` | `91ca8299fbb1e7f0` |
| PR AUC | 0.9019 | 0.8240 | 0.8256 | 0.8267 |
| ROC AUC | 0.9290 | 0.9056 | 0.9145 | 0.9201 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
