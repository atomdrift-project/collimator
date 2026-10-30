# Confirm FAIL — f772c8088cf3a7dc on `filetypes/nupkg`

Cycle `20261030T193235-confirm-f772c8088cf3a7dc` — 2026-10-30T19:32:35Z

averaged ensemble PR_AUC regressed: 0.8723 -> 0.8607 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `f772c8088cf3a7dc` | `93b1f967ccd8223b` | `93b1f967ccd8223b` | `93b1f967ccd8223b` |
| PR AUC | 0.8723 | 0.8677 | 0.8526 | 0.8519 |
| ROC AUC | 0.9915 | 0.9928 | 0.9948 | 0.9903 |
| Recall@L50 | — | 0.7692 | 0.7692 | 0.6923 |
| verdict | — | PASS | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (1/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
