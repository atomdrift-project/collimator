# Confirm FAIL — ff59baa1ca4baee2 on `filetypes/deb`

Cycle `20261102T190122-confirm-ff59baa1ca4baee2` — 2026-11-02T19:01:22Z

confirmation tied L25 recall but lost zero-FP recall

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ff59baa1ca4baee2` | `ca8562779f64670f` | `ca8562779f64670f` | `ca8562779f64670f` |
| PR AUC | 0.6287 | 0.6063 | 0.6454 | 0.6083 |
| ROC AUC | 0.9971 | 0.9885 | 0.9953 | 0.9980 |
| Recall@L50 | — | — | 0.0667 | — |
| verdict | — | FAIL | PASS | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
