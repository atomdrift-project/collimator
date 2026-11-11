# Confirm FAIL — 752264831d149710 on `filetypes/csharp`

Cycle `20261110T195512-confirm-752264831d149710` — 2026-11-10T19:55:12Z

confirmation measured L25 recall regressed: 0.58981 -> 0.48058

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `752264831d149710` | `fb8f55bd696dd215` | `fb8f55bd696dd215` | `fb8f55bd696dd215` |
| PR AUC | 0.9707 | 0.9729 | 0.9715 | 0.9708 |
| ROC AUC | 0.9986 | 0.9986 | 0.9986 | 0.9985 |
| Recall@L50 | — | 0.4369 | 0.3956 | 0.4053 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
