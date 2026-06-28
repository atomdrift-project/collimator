# Confirm FAIL — ad59d38e94de263d on `filetypes/powershell`

Cycle `20260628T130234-confirm-ad59d38e94de263d` — 2026-06-28T13:02:34Z

averaged ensemble PR_AUC regressed: 0.9933 -> 0.9879 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ad59d38e94de263d` | `283b4d09aea32ae5` | `283b4d09aea32ae5` | `283b4d09aea32ae5` |
| PR AUC | 0.9933 | 0.9878 | 0.9875 | 0.9879 |
| ROC AUC | 0.9836 | 0.9788 | 0.9787 | 0.9789 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
