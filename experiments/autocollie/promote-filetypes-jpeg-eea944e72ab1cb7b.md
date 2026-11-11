# Promote REJECTED — `eea944e72ab1cb7b` on `filetypes/jpeg`

Generated 2026-11-10T19:55:12Z

confirm did not hold: confirmation measured L25 recall regressed: 0.46622 -> 0.43919

## Gates

- **Confirm** (different seed, original profile): **FAIL** — confirmation measured L25 recall regressed: 0.46622 -> 0.43919
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `eea944e72ab1cb7b` | `2dfd1de775e9e62b` | `—` |
| PR AUC | 0.8703 | 0.9057 | — |
| ROC AUC | 0.9932 | 0.9940 | — |
| F1 | 0.3086 | 0.5490 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: confirmation measured L25 recall regressed: 0.46622 -> 0.43919
