# Confirm FAIL — a00e714c34e99515 on `filetypes/asp`

Cycle `20261112T202527-confirm-a00e714c34e99515` — 2026-11-12T20:25:27Z

confirmation tied L25 recall but lost zero-FP recall

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `a00e714c34e99515` | `a3c1c475ce121b3f` | `a3c1c475ce121b3f` | `a3c1c475ce121b3f` |
| PR AUC | 0.9938 | 0.9954 | 0.9902 | 0.9920 |
| ROC AUC | 0.9860 | 0.9900 | 0.9780 | 0.9820 |
| Recall@L50 | — | 0.9200 | 0.8000 | 0.8400 |
| verdict | — | PASS | PASS | PASS |

## Disposition

This spec did not survive multi-seed reseeding (3/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
