# Confirm FAIL — 3f1317631eaf6127 on `filetypes/applescript`

Cycle `20261102T221457-confirm-3f1317631eaf6127` — 2026-11-02T22:14:57Z

averaged ensemble PR_AUC regressed: 0.7459 -> 0.7203 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `3f1317631eaf6127` | `951439912502aa44` | `951439912502aa44` | `951439912502aa44` |
| PR AUC | 0.7459 | 0.7368 | 0.7331 | 0.7203 |
| ROC AUC | 0.9745 | 0.9740 | 0.9740 | 0.9729 |
| Recall@L50 | — | 0.1538 | 0.1538 | 0.0769 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
