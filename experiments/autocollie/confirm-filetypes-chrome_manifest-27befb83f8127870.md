# Confirm FAIL — 27befb83f8127870 on `filetypes/chrome_manifest`

Cycle `20261110T195452-confirm-27befb83f8127870` — 2026-11-10T19:54:52Z

averaged ensemble PR_AUC regressed: 0.9889 -> 0.9765 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `27befb83f8127870` | `ef126ca0811a3812` | `ef126ca0811a3812` | `ef126ca0811a3812` |
| PR AUC | 0.9889 | 0.9396 | 0.9889 | 0.9354 |
| ROC AUC | 0.9992 | 0.9950 | 0.9992 | 0.9925 |
| Recall@L50 | — | 0.6667 | 0.8889 | 0.7778 |
| verdict | — | FAIL | PASS | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
