# Confirm FAIL — 36fbe0e3e4e6f816 on `filetypes/plist`

Cycle `20261030T191624-confirm-36fbe0e3e4e6f816` — 2026-10-30T19:16:24Z

confirmation measured L25 recall regressed: 0.49057 -> 0.39623

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `36fbe0e3e4e6f816` | `6b72a4f22084c0ca` | `6b72a4f22084c0ca` | `6b72a4f22084c0ca` |
| PR AUC | 0.8053 | 0.8307 | 0.8328 | 0.8418 |
| ROC AUC | 0.9985 | 0.9782 | 0.9974 | 0.9943 |
| Recall@L50 | — | 0.4151 | 0.3585 | 0.3585 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
