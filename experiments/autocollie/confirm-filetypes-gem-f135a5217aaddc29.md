# Confirm FAIL — f135a5217aaddc29 on `filetypes/gem`

Cycle `20261029T125324-confirm-f135a5217aaddc29` — 2026-10-29T12:53:24Z

averaged ensemble PR_AUC regressed: 0.9156 -> 0.9074 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f135a5217aaddc29` | `af0a8107ea91b163` | `af0a8107ea91b163` | `af0a8107ea91b163` |
| PR AUC | 0.9156 | 0.8493 | 0.9085 | 0.9075 |
| ROC AUC | 0.9836 | 0.9724 | 0.9875 | 0.9908 |
| Recall@L50 | — | 0.0921 | 0.8684 | 0.8816 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
