# Confirm FAIL — 107889095c2ad603 on `filetypes/apk_android`

Cycle `20261030T214456-confirm-107889095c2ad603` — 2026-10-30T21:44:56Z

confirmation measured L25 recall regressed: 0.98013 -> 0.97682

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `107889095c2ad603` | `0e220736a22407fc` | `0e220736a22407fc` | `0e220736a22407fc` |
| PR AUC | 0.9992 | 0.9994 | 0.9995 | 0.9992 |
| ROC AUC | 0.9956 | 0.9967 | 0.9975 | 0.9958 |
| Recall@L50 | — | 0.9404 | 0.9007 | 0.9172 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
