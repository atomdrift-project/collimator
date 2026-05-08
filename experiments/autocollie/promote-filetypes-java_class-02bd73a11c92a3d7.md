# Promote REJECTED — `02bd73a11c92a3d7` on `filetypes/java_class`

Generated 2026-05-08T20:35:29Z

F1 regressed at full-train: 0.9922 -> 0.9764

## Gates

- **Confirm** (different seed, original profile): **PASS** — F1 held across 3 seeds (orig 0.9922)
- **Full-train** (inflated profile, original seed): **REJECTED** — see metrics below

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `02bd73a11c92a3d7` | `2a519bbf2266f883` | `13a69eff3b5b3242` |
| F1 | 0.9922 | 0.9924 | 0.9764 |
| ROC AUC | 1.0000 | 1.0000 | 1.0000 |
| AP | — | — | — |
| recall@3 FP/M (screen) | 1.0000 | 1.0000 | 1.0000 |
| recall@FP=0 (full-train) | — | — | — |
| recall@FP=5 (full-train) | — | — | — |

## Disposition

This spec did not survive the promotion ladder.

F1 regressed at full-train: 0.9922 -> 0.9764
