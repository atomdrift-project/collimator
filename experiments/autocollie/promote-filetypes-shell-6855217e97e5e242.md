# Promote REJECTED — `6855217e97e5e242` on `filetypes/shell`

Generated 2026-11-06T11:25:29Z

confirm did not hold: confirmation measured L25 recall regressed: 0.86386 -> 0.85266

## Gates

- **Confirm** (different seed, original profile): **FAIL** — confirmation measured L25 recall regressed: 0.86386 -> 0.85266
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `6855217e97e5e242` | `f579661c29a8ffc6` | `—` |
| PR AUC | 0.9935 | 0.9956 | — |
| ROC AUC | 0.9977 | 0.9983 | — |
| F1 | 0.9640 | 0.9773 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: confirmation measured L25 recall regressed: 0.86386 -> 0.85266
