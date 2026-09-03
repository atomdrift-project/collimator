# Confirm FAIL — f275f9c857491d84 on `filetypes/json`

Cycle `20260824T234629-confirm-f275f9c857491d84` — 2026-08-24T23:46:29Z

averaged ensemble PR_AUC regressed: 0.1857 -> 0.0725 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f275f9c857491d84` | `92644948441ba52d` | `92644948441ba52d` | `92644948441ba52d` |
| PR AUC | 0.1857 | 0.0632 | 0.0577 | 0.0786 |
| ROC AUC | 0.7468 | 0.6064 | 0.5658 | 0.7332 |
| Recall@L50 | — | 0.1379 | 0.1330 | 0.1379 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
