# Promote REJECTED — `bb8825a47ea45b53` on `filetypes/package.json`

Generated 2026-10-30T13:31:12Z

confirm did not hold: confirmation measured L25 recall regressed: 0.79153 -> 0.77597

## Gates

- **Confirm** (different seed, original profile): **FAIL** — confirmation measured L25 recall regressed: 0.79153 -> 0.77597
- **Full-train**: not run (confirm gate failed)

## Metrics

| | original (screen) | confirm (seed=43) | full-train (samples=600000) |
|---|---|---|---|
| key | `bb8825a47ea45b53` | `f81a2bb6fd33751a` | `—` |
| PR AUC | 0.9776 | 0.9772 | — |
| ROC AUC | 0.9824 | 0.9815 | — |
| F1 | 0.9612 | 0.9748 | — |

## Disposition

This spec did not survive the promotion ladder.

confirm did not hold: confirmation measured L25 recall regressed: 0.79153 -> 0.77597
