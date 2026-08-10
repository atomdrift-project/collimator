# Confirm FAIL — ee9d8950d4c567e9 on `filegroups/source`

Cycle `20260805T003620-confirm-ee9d8950d4c567e9` — 2026-08-05T00:36:20Z

averaged ensemble PR_AUC regressed: 0.9337 -> 0.6715 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `ee9d8950d4c567e9` | `18a51bcc6090a546` | `18a51bcc6090a546` | `18a51bcc6090a546` |
| PR AUC | 0.9337 | 0.6651 | 0.6750 | 0.6615 |
| ROC AUC | 0.9210 | 0.9253 | 0.9271 | 0.9209 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
