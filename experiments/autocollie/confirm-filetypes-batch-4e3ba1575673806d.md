# Confirm FAIL — 4e3ba1575673806d on `filetypes/batch`

Cycle `20261030T231434-confirm-4e3ba1575673806d` — 2026-10-30T23:14:34Z

confirmation measured L25 recall regressed: 0.98240 -> 0.98060

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `4e3ba1575673806d` | `73979214f9eed80f` | `73979214f9eed80f` | `73979214f9eed80f` |
| PR AUC | 1.0000 | 0.9999 | 1.0000 | 1.0000 |
| ROC AUC | 0.9996 | 0.9995 | 0.9996 | 0.9996 |
| Recall@L50 | — | 0.9802 | 0.9802 | 0.9813 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
