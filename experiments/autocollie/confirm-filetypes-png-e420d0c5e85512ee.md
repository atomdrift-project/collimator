# Confirm FAIL — e420d0c5e85512ee on `filetypes/png`

Cycle `20260703T025641-confirm-e420d0c5e85512ee` — 2026-07-03T02:56:41Z

averaged ensemble PR_AUC regressed: 0.2874 -> 0.0891 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `e420d0c5e85512ee` | `0a16dc1d7ae928e6` | `0a16dc1d7ae928e6` | `0a16dc1d7ae928e6` |
| PR AUC | 0.2874 | 0.0852 | 0.0891 | 0.0860 |
| ROC AUC | 0.7125 | 0.4282 | 0.4745 | 0.4669 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
