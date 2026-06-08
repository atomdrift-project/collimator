# Confirm FAIL — 859d578ae91ea04d on `filegroups/source`

Cycle `20260608T161025-confirm-859d578ae91ea04d` — 2026-06-08T16:10:25Z

averaged ensemble PR_AUC regressed: 0.9051 -> 0.6478 (tol 0.0050, K=3)

## Per-seed results (3 ran)

| | original | seed=43 | seed=44 | seed=45 | 
|---|---|---|---|---|
| key | `859d578ae91ea04d` | `aaa3d9d0dba741c9` | `aaa3d9d0dba741c9` | `aaa3d9d0dba741c9` |
| PR AUC | 0.9051 | 0.5977 | 0.6547 | 0.6393 |
| ROC AUC | 0.9126 | 0.8987 | 0.9206 | 0.9119 |
| Recall@3FPM | — | 0.0000 | 0.0000 | 0.0000 |
| verdict | — | FAIL | FAIL | FAIL |

## Disposition

This spec did not survive multi-seed reseeding (0/3 held). Suggest abandoning the idea or letting the LLM propose a variant.
