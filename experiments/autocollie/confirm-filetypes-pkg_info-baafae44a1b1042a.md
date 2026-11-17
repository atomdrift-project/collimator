# Confirm FAIL — baafae44a1b1042a on `filetypes/pkg_info`

Cycle `20261112T203935-confirm-baafae44a1b1042a` — 2026-11-12T20:39:35Z

confirmation measured L25 recall regressed: 0.75000 -> 0.71875

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `baafae44a1b1042a` | `971c97aa441ca76f` | `971c97aa441ca76f` | `971c97aa441ca76f` |
| PR AUC | 0.8709 | 0.8709 | 0.8708 | 0.8715 |
| ROC AUC | 0.9739 | 0.9739 | 0.9750 | 0.9846 |
| Recall@L50 | — | 0.5625 | 0.5312 | 0.6250 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
