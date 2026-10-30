# Promote REJECTED — `f772c8088cf3a7dc` on `filetypes/nupkg`

Generated 2026-10-30T19:33:03Z

confirm did not hold: averaged ensemble PR_AUC regressed: 0.8723 -> 0.8607 (tol 0.0050, K=3)

## Gates

- **Confirm** (different seed, original profile): **FAIL** — averaged ensemble PR_AUC regressed: 0.8723 -> 0.8607 (tol 0.0050, K=3)
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `f772c8088cf3a7dc` | `93b1f967ccd8223b` | `—` |
| PR AUC | 0.8723 | 0.8607 | — |
| ROC AUC | 0.9915 | 0.9936 | — |
| F1 | 0.7857 | 0.8696 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: averaged ensemble PR_AUC regressed: 0.8723 -> 0.8607 (tol 0.0050, K=3)
