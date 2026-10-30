# Confirm FAIL — c3173597aebc41be on `filetypes/vsix`

Cycle `20261030T192918-confirm-c3173597aebc41be` — 2026-10-30T19:29:18Z

confirmation tied L25 recall but lost zero-FP recall

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `c3173597aebc41be` | `c5539dbcc2427b53` | `c5539dbcc2427b53` | `c5539dbcc2427b53` |
| PR AUC | 0.6291 | 0.6238 | 0.6325 | 0.6496 |
| ROC AUC | 0.8891 | 0.9120 | 0.9099 | 0.9151 |
| Recall@L50 | — | 0.2619 | 0.2857 | 0.3333 |
| verdict | — | FAIL | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (2/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
