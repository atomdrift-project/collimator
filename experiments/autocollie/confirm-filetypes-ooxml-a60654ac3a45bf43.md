# Confirm FAIL — a60654ac3a45bf43 on `filetypes/ooxml`

Cycle `20261029T125156-confirm-a60654ac3a45bf43` — 2026-10-29T12:51:56Z

confirmation measured L25 recall regressed: 0.35919 -> 0.35896

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a60654ac3a45bf43` | `b43ea356dfb9c63a` | `b43ea356dfb9c63a` | `b43ea356dfb9c63a` |
| PR AUC | 0.9810 | 0.9816 | 0.9552 | 0.9548 |
| ROC AUC | 0.8632 | 0.8655 | 0.7044 | 0.7015 |
| Recall@L50 | — | 0.3497 | 0.3288 | 0.3391 |
| verdict | — | PASS | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
