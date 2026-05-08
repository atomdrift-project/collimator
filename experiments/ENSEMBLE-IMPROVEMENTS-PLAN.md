# Plan: Best-Possible Ensemble Numbers + L3 Detection on Small Corpora

Five workstreams, ordered by ratio of impact to effort. Items 1, 2, 3, 5 are this
session's work; item 4 is corpus-growth that the human is collecting separately.

The throughline: **separate ranking quality from operational thresholding.**
Right now both share a single calibration corpus, which is fine for big routes
(pe, elf, javascript with millions of benigns) but breaks at small N where
a 3 FP/M threshold isn't statistically resolvable.

---

## Item 2 — Stacked LR combiner (impact: medium, effort: small)

### Problem
`calibrated_max` is the simplest combiner that respects per-route score scales,
but it can't capture **complementarity** across routes — cases where the
specialist is weak, the general is also weak, but the *combination* is
informative. PDF (specialist 0.49, general 0.55, ensemble 0.62) hints there's
more signal we're leaving on the table.

### Approach
Train a per-filetype logistic regression on `(general_score, group_score,
specialist_score)` against the row's label, fit with 5-fold CV (no leakage),
on the test bucket. Add as a third strategy in the picker; it competes with
`specialist_priority` and `calibrated_max`.

### Implementation
- ~80 LoC in `compute_routed_metrics.py`
- New helper `_ensemble_scores_stacked_lr` parallel to the existing strategies
- Picker already chooses max ROC AUC across strategies; LR will win where
  cross-route signal genuinely complements the specialist
- Fall back to existing strategies when LR can't fit (e.g., one class missing)

### Success criteria
- Every filetype: `ensemble ≥ specialist` still holds
- Filetypes with weak specialists (pdf, xml, gz, kotlin) show LR winning the
  picker with a measurable lift
- Filetypes with strong specialists (pe, elf, javascript): picker stays on
  `specialist_priority`; LR ties or loses by < 0.001 ROC

---

## Item 5 — Bayesian threshold smoothing (impact: small-medium, effort: small)

### Problem
Empirical threshold-at-3-FPM with N=200 benigns has 95% CI from ~0 to ~12 FP/M.
Empirical estimators are point estimates with no uncertainty; we deploy as if
the threshold is exact when it's actually quite noisy on small routes.

### Approach
Beta-Binomial prior on per-bin FP rate. Given a candidate threshold producing
k FPs in N benigns, the posterior FP rate is Beta(k+α, N-k+β) — instead of
returning a single threshold, return the threshold that minimizes upper-credible-
bound FP rate (conservative deploy) or maximizes recall at the lower-credible-
bound (aggressive). Default to MAP (= empirical) for backward compat.

### Implementation
- ~50 LoC additive in `src/collimator/thresholds.py` next to
  `_select_threshold_at_fp_budget`
- New optional argument: `prior: BetaBinomialPrior | None` (default None ⇒
  empirical)
- New function `select_threshold_at_credible_bound(scores, labels, target,
  alpha=0.05, side='upper')`
- Wire into `azoth_calibrate_ensemble.py` as opt-in via
  `--threshold-credible-bound upper|map|lower` flag

### Success criteria
- Existing behavior unchanged when flag absent (backward compat)
- On small-N routes (msi, rtf, powershell), upper-bound threshold is
  consistently stricter than MAP (because we admit FP-rate uncertainty)
- Unit tests verify Beta-Binomial math

---

## Item 3 — Skill prompts + autocollie hints for low-FPR optimization (impact: medium, effort: small)

### Problem
Pi has access to `scale_pos_weight_mult`, `boosting_type=dart`, `extra_trees`,
and threshold-mode knobs we added during this session. But it rarely sweeps
them — the skill has the knobs in the allowlist but no strong "use these on
weak L3 routes" signal in the proposal-generation guidance.

### Approach
Update `skill.md` to:
- Identify weak-L3 routes from the prompt's prior-runs context (recall@k FP/M
  reads as 0.0 across multiple specs ⇒ weak L3)
- Mandate at least one `scale_pos_weight_mult ∈ {0.25, 0.5, 0.75}` sweep when
  weak-L3 is detected
- Suggest combining `boosting_type=dart` with low `scale_pos_weight_mult` for
  routes with known calibration trouble

Also: add a new prompt section showing each route's `n_benigns` and the
implied `min_observable_fp_per_million`, so pi understands at a glance which
routes are corpus-bound vs which are model-bound.

### Implementation
- `skill.md` prose updates (~30 lines)
- `internal/specs/prompt.go` — add a "Route corpus characteristics" section
  derived from the route's prior runs' `n_benign_holdout` field (~50 LoC)

### Success criteria
- Pi proposes `scale_pos_weight_mult` sweeps on at least 50% of weak-L3 routes
- Pi explains its choice referencing benign sample size where appropriate
- No regression on strong-L3 routes (pi shouldn't reach for these knobs when
  they're not needed)

---

## Item 1 — Cross-family benign pool for FP estimation (impact: high, effort: medium-high)

### Problem
**The killer issue.** Small-corpus routes (msi 18 benigns, rtf 51, powershell
159) cannot have L3 thresholds reliably calibrated because the smallest
empirical FPR is `1/N`, well above the 3 FP/M target. This is why those routes
deploy as `no_policy` even though their raw discrimination is excellent.

### Approach
For each route's threshold search, **estimate FP rate against an extended
benign pool**, not just the route's own benigns:
- *Family pool*: benigns from the route's filegroup (e.g., msi gets all
  native-family benigns: elf + macho + msi + pe ≈ 700k benigns)
- This requires the route's specialist to have *scores* for those extended
  benigns, which today's score_table doesn't include
- Therefore: extend the score_table generation to score each specialist on
  its filegroup's full benign pool, not just its own filetype's benigns

**Conceptual validity**: a sharp specialist should give low scores to its
filegroup-peers' benigns (otherwise it's overfitting). A specialist that
gives high scores to its peer filetypes' benigns is a specialist that would
fail in production anyway, so detecting that during calibration is a feature.

**Risk**: cross-family benigns may not be representative of *deployed* benign
distribution for that route. We address this by limiting expansion to the
filegroup, not the entire corpus.

### Implementation
- Modify `_fetch_rows` in `azoth_calibrate_ensemble.py`: for each route, fetch
  benigns matching `file_group(route)`, not just `file_type(route)`. Malware
  side stays route-only.
- New flag: `--fp-pool-mode {route_only, family_pool}` defaulting to
  `family_pool` for routes with < 50k own benigns. Above that threshold, the
  route's own pool is statistically sufficient.
- The score table grows: extra route × extra-benign columns. Estimate +30-50%
  size.
- `_select_threshold_at_fp_budget` needs to be aware that some rows in the
  benign pool aren't from this route's *own* filetypes — used only for FP
  rate estimation, not for recall (the malware side is still route-filtered).
- Combine with item 5 (Bayesian smoothing) for routes that still have small
  family pools (e.g., msi family is small; documents family is small).

### Success criteria
- msi, rtf, powershell, batch: L3 hostile policy is no longer `no_policy` —
  they get a real threshold derived from the family pool
- Per-route reports show the augmented FP pool size and family used
- No regression for big-corpus routes (pe, elf, javascript): `route_only` mode
  matches existing behavior byte-identically
- Cross-route smoke test: msi specialist score distribution on native-family
  benigns is investigated; if it's clearly out-of-distribution, fall back to
  smaller scope or document the limit

---

## Item 4 — Corpus growth (human-driven; documented here for visibility)

The routes with chronically small benign pools — and therefore intrinsically
unreliable L3 calibration regardless of #1 — are listed below. Listed in order
of "would benefit most from more data":

| Route | Benigns (approx) | Bottleneck |
|---|---:|---|
| `msi` | ~150 | Sample collection from clean Windows installer corpora |
| `rtf` | ~400 | Sample collection from legitimate Office RTF corpora |
| `powershell` | ~1500 | More legitimate PowerShell from CI/CD, IT scripts |
| `batch` | ~2000 | More legitimate `.bat` from Windows admin scripts |
| `pdf` | ~3000 | Massive miss — PDF is high-volume; pull from clean PDF corpora |
| `vbs` | ~800 | More legitimate VBS from Office macros |
| `chrome-manifest` | ~100 | Most files are tiny; could pull from CWS/AMO |
| `github-actions` | ~3500 | Healthy growth; pull from public repos |

For each route, we'd want at least 100k benigns to support:
- Reliable L3 calibration without family-pool augmentation
- Adequate train/holdout split for the specialist
- Stable per-route AUC measurements (currently noisy at small N)

---

## Dependencies and order

```
       [ #2 stacked LR ]   ← independent, easy, do first
              │
       [ #5 Bayesian ]     ← independent, easy, do parallel
              │
       [ #3 skill+prompt ] ← independent, prose, do parallel
              │
       [ #1 family pool ]  ← depends on rebuilding score_table; do last
              │
              ▼
[ regenerate per_filetype_metrics + READMEs ]
```

Each item ships its own tests where applicable. After all four are done, a
single re-run of `make azoth-validate` (which now invokes
`compute_routed_metrics.py` and `write_azoth_readmes.py`) produces the
updated bundle with refreshed metrics and READMEs.

#4 is on the human; this plan flags exactly which routes need data and
roughly how much.
