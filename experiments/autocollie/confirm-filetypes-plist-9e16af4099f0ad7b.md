# Confirm FAIL — 9e16af4099f0ad7b on `filetypes/plist`

Cycle `20260705T163015-confirm-9e16af4099f0ad7b` — 2026-07-05T16:30:15Z

averaged ensemble PR_AUC regressed: 0.1040 -> 0.0105 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `9e16af4099f0ad7b` | `6cc3461e6e7af3c4` | `6cc3461e6e7af3c4` | `6cc3461e6e7af3c4` |
| PR AUC | 0.1040 | 0.0105 | 0.0105 | 0.0105 |
| ROC AUC | 0.6766 | 0.5113 | 0.5092 | 0.5113 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
