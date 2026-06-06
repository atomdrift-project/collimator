# Confirm FAIL — 919e3b08bc695b05 on `filegroups/portable`

Cycle `20260606T133523-confirm-919e3b08bc695b05` — 2026-06-06T13:35:23Z

averaged ensemble PR_AUC regressed: 0.9382 -> 0.9172 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `919e3b08bc695b05` | `1bfd096d337e75fa` | `1bfd096d337e75fa` | `1bfd096d337e75fa` |
| PR AUC | 0.9382 | 0.9168 | 0.9041 | 0.9150 |
| ROC AUC | 0.9757 | 0.9518 | 0.9737 | 0.9570 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
