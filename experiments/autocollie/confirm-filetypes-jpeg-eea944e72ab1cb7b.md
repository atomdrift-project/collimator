# Confirm FAIL — eea944e72ab1cb7b on `filetypes/jpeg`

Cycle `20261110T195456-confirm-eea944e72ab1cb7b` — 2026-11-10T19:54:56Z

confirmation measured L25 recall regressed: 0.46622 -> 0.43919

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `eea944e72ab1cb7b` | `2dfd1de775e9e62b` | `2dfd1de775e9e62b` | `2dfd1de775e9e62b` |
| PR AUC | 0.8703 | 0.8956 | 0.8975 | 0.8881 |
| ROC AUC | 0.9932 | 0.9943 | 0.9924 | 0.9933 |
| Recall@L50 | — | 0.2905 | 0.3581 | 0.4730 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
