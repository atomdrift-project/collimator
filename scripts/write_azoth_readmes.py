#!/usr/bin/env python3
"""Write concise README files for an Azoth model bundle."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Any

# scripts/ isn't on sys.path; reach src/ for `collimator.bundle`.
_SRC = Path(__file__).resolve().parent.parent / "src"
if str(_SRC) not in sys.path:
    sys.path.insert(0, str(_SRC))
# scripts/ also isn't a package; pull the CP helper from the calibrate script.
_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from collimator import bundle  # noqa: E402  — late import after sys.path patch
from azoth_calibrate_ensemble import _clopper_pearson_fp_per_million_upper  # noqa: E402


def _pct(value: Any) -> str:
    if value is None:
        return "-"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "-"
    if math.isnan(numeric):
        return "-"
    return f"{numeric * 100:.2f}%"


def _num(value: Any, digits: int = 6) -> str:
    if value is None:
        return "-"
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "-"
    if math.isnan(numeric):
        return "-"
    if abs(numeric) >= 1000:
        return f"{numeric:.1f}"
    return f"{numeric:.{digits}f}"


def _int(value: Any) -> str:
    return "-" if value is None else f"{int(value):,}"


def _short_hash(value: Any) -> str:
    if not value:
        return "-"
    return str(value)[:12]


# EMBER 2024 Table 5 reference values (Joyce et al., KDD'25).
# https://doi.org/10.1145/3711896.3737431
# Each entry is a single LightGBM classifier; we use them for apples-to-apples
# delta reporting in our model cards.  Their "All files" row maps to our
# `general` model's all-corpus score; their "<X> files → <X> files" row maps
# to our `filetypes/<X>` specialist evaluated on its own holdout.  Filetypes
# without a clean mapping (e.g. EMBER's APK has no direct route in our bundle)
# are omitted.
EMBER_2024 = {
    "all_files": {
        "general":    {"roc_auc": 0.9969, "pr_auc": 0.9971},
    },
    # PE: EMBER reports per-PE-subtype (Win32/Win64/.NET) plus an "All PE
    # files" aggregate.  Our `filetypes/pe` route covers all PE subtypes, so
    # we compare against the aggregate.
    "pe": {
        "general":    {"roc_auc": 0.9982, "pr_auc": 0.9983, "label": "All PE files (general)"},
        "specialist": {"roc_auc": 0.9982, "pr_auc": 0.9983, "label": "All PE files (specialist)"},
    },
    "elf": {
        "general":    {"roc_auc": 0.9887, "pr_auc": 0.9902, "label": "All files → ELF"},
        "specialist": {"roc_auc": 0.9933, "pr_auc": 0.9933, "label": "ELF specialist"},
    },
    "pdf": {
        "general":    {"roc_auc": 0.9878, "pr_auc": 0.9901, "label": "All files → PDF"},
        "specialist": {"roc_auc": 0.9912, "pr_auc": 0.9933, "label": "PDF specialist"},
    },
}


def _delta(ours: float | None, theirs: float | None) -> str:
    """Format `ours - theirs` with sign (+ / -) for direct comparison.

    6 decimals so saturated-curve deltas (e.g. +0.000018 PR AUC over
    EMBER) don't round to +0.0000 and read as "no improvement."
    """
    if ours is None or theirs is None:
        return "-"
    try:
        d = float(ours) - float(theirs)
    except (TypeError, ValueError):
        return "-"
    if math.isnan(d):
        return "-"
    sign = "+" if d >= 0 else ""
    return f"{sign}{d:.6f}"


def _ember_for(filetype: str, view: str) -> dict[str, float] | None:
    """Look up EMBER 2024 reference for a (filetype, view) pair.  view is one
    of {'general', 'specialist'}.  Returns None when no published value
    matches our route."""
    bucket = EMBER_2024.get(filetype)
    if not bucket:
        return None
    return bucket.get(view)


def _load_per_filetype_metrics(root: Path) -> dict[str, Any]:
    """Load the routed-ensemble metrics produced by compute_routed_metrics.py.
    Returns an empty dict (with empty 'filetypes') when the file is missing —
    the caller can still emit a README, just without the new tables."""
    path = root / "per_filetype_metrics.json"
    if not path.exists():
        return {"filetypes": {}, "filegroups": {}, "all_files": {}}
    with open(path) as f:
        return json.load(f)


def _load_deployed_eval(root: Path) -> dict[str, Any]:
    """Load route_policy_eval_oof.json — the deployed OR-rule / blend
    measured per filetype per level on the locked test partition. This
    is the source of truth for what litmus actually flags. Returns an
    empty shape when missing so the writer can still produce a README."""
    path = root / "route_policy_eval_oof.json"
    if not path.exists():
        return {"filetypes": {}}
    with open(path) as f:
        return json.load(f)


# Filetypes to surface in the headline tables.  Curated for supply-chain
# security and security-engineering readers — 15 routes balanced across:
#
#   native binaries (4):    pe, elf, macho, msi
#   documents (2):          pdf, rtf
#   scripts (5):            javascript, python, shell, powershell, batch
#   package ecosystems (2): package.json (npm manifest), jar (JVM archive)
#   other (2):              ruby (RubyGems), perl (CI/CD)
#
# Order is by deploy/attack frequency: binaries first, then documents,
# then scripts (with the ps1/bat/sh trio kept adjacent), then ecosystem
# manifests.  EMBER 2024 reference exists only for pe/elf/pdf — others
# show ROC/PR/F1 alone.
HEADLINE_FILETYPES = (
    "pe", "elf", "macho", "msi",                       # native binaries
    "pdf", "rtf",                                      # documents
    "javascript", "python", "shell", "powershell", "batch",  # scripts
    "package.json", "jar",                             # package ecosystems
    "ruby", "perl",                                    # other script ecosystems
)


# Pure-container archive types: scored only by the general model on the
# outer wrapper, since the actual malicious content is a nested member
# the ensemble already classifies under its own filetype. Excluded from
# the headline because the wrapper's score is incidental, not a model
# quality signal. ``data``/``unknown`` are excluded for the same reason —
# they collect rows whose filetype couldn't be identified.
_HEADLINE_EXCLUDE: frozenset[str] = frozenset({
    "data", "unknown",
    "zip", "tar", "tar.gz", "tar.bz2", "tar.xz", "tar.zst",
    "7z", "gz", "bz2", "xz", "zst", "rar",
})


def _headline_filetypes(
    metrics: dict[str, Any],
    config: dict[str, Any] | None = None,
    eval_data: dict[str, Any] | None = None,
    *,
    level: int = 3,
    severity: str = "hostile",
) -> tuple[str, ...]:
    """Pick filetypes for the bundle README's headline table.

    Inclusion: at least 25 malware AND 25 benign in test, OR at least 100
    of each in the full labeled corpus (covers small-test-slice filetypes
    where the model still has plenty of training signal). Sort:
    recall@3FP/M descending — same metric the picker optimizes for, so
    the table opens with the filetypes the deployed system actually
    catches the most malware on at our FP budget. PR AUC tiebreaks for
    determinism.

    Filetypes in ``_HEADLINE_EXCLUDE`` (data, unknown, pure archive
    wrappers) are skipped — their score reflects outer-container shape,
    not classifier quality. ``eval_data`` is unused but kept in the
    signature for backward compatibility with callers that pass it.
    """
    del eval_data, level, severity  # see docstring — kept for back-compat only
    ft_dict = (metrics or {}).get("filetypes", {})
    models_by_route = {
        mo.get("route"): mo
        for mo in ((config or {}).get("models") or [])
    }

    def qualifies(ft: str, entry: dict[str, Any]) -> bool:
        if ft in _HEADLINE_EXCLUDE:
            return False
        t_mal = entry.get("n_malware", 0) or 0
        t_ben = entry.get("n_benign", 0) or 0
        if t_mal >= 25 and t_ben >= 25:
            return True
        mo = models_by_route.get(f"filetypes/{ft}") or {}
        if (mo.get("malware") or 0) >= 100 and (mo.get("benign") or 0) >= 100:
            return True
        return False

    def sort_key(item: tuple[str, dict[str, Any]]) -> tuple[float, float, str]:
        ft, entry = item
        ens = entry.get("ensemble") or {}
        r3 = ens.get("recall_at_3fp_per_million")
        pr = ens.get("pr_auc")
        if not isinstance(r3, (int, float)) or (isinstance(r3, float) and math.isnan(r3)):
            r3 = 0.0
        if not isinstance(pr, (int, float)):
            pr = 0.0
        # Sort by recall@3FP/M desc, PR AUC desc tiebreak, then ft for
        # determinism. Mirrors the picker's selection key.
        return (-float(r3), -float(pr), ft)

    candidates = [
        (ft, entry) for ft, entry in ft_dict.items() if qualifies(ft, entry)
    ]
    candidates.sort(key=sort_key)
    return tuple(ft for ft, _ in candidates)


def _metric_cell(
    point: Any, low: Any, high: Any,
    *, include_ci: bool = True, as_percent: bool = False,
) -> str:
    """Render `point [low, high]` for a metric with bootstrap CI; collapses to
    bare point if CI fields aren't populated (small-corpus / single-class).
    Returns "—" for missing or NaN points.

    ``as_percent=True`` formats as a percentage (e.g., recall: 0.9355 →
    "93.55%"). Used for recall, F1 — proportions that are easier to scan
    than 4-decimal floats.

    AUCs use 6 decimals so saturated-curve values like 0.999981 don't
    round to 1.0000 and obscure how much headroom is left. Most routes
    sit at 0.99x where 6 decimals is just trailing zeros; the few that
    hit the four-nines tail are exactly where the extra precision matters.
    """
    if point is None:
        return "—"
    try:
        numeric = float(point)
    except (TypeError, ValueError):
        return "—"
    if math.isnan(numeric):
        return "—"
    fmt = (lambda v: f"{float(v) * 100:.2f}%") if as_percent else (lambda v: _num(v, 6))
    base = fmt(numeric)
    if not include_ci or low is None or high is None:
        return base
    return f"{base} [{fmt(low)}, {fmt(high)}]"


def _ensemble_table(
    metrics: dict[str, Any],
    eval_data: dict[str, Any],
    filetypes: tuple[str, ...],
    *,
    link_routes: bool = False,
) -> list[str]:
    """Headline table for the routed ensemble's model properties.

    Reports PR AUC, ROC AUC, F1, and Recall@3FP/M from
    ``per_filetype_metrics.json["filetypes"][<ft>]["ensemble"]`` — the
    selected combiner's per-filetype slice numbers on the locked test
    partition. These are properties of the MODEL: how well its scores
    rank malware vs benign, independent of how litmus chooses to use
    them at scan time.

    Litmus's runtime policy (which severity level fires, which OR-rule
    or blend is deployed, etc.) is reported in `route_policies.md` and
    `slice_metrics.md`. It's a downstream consumer concern, not an
    azoth model property.

    ``eval_data`` is accepted for backward compatibility with callers
    that pre-load it; the headline doesn't read from it anymore.
    """
    lines = [
        "| File type | Test mal / ben | PR AUC | ROC AUC | F1 | Recall @ 3FP/M | Δ vs EMBER 2024 |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for ft in filetypes:
        m_entry = metrics.get("filetypes", {}).get(ft) or {}
        if not m_entry:
            continue
        ens = m_entry.get("ensemble") or {}
        n_mal = m_entry.get("n_malware")
        n_ben = m_entry.get("n_benign")
        ember = _ember_for(ft, "specialist")
        ens_pr = ens.get("pr_auc")
        ens_roc = ens.get("roc_auc")
        ens_f1 = ens.get("f1")
        ens_recall = ens.get("recall_at_3fp_per_million")
        if ens_pr is None and ens_roc is None:
            pr_str = roc_str = f1_str = recall_str = "—"
            ember_str = "—"
        else:
            pr_str = _metric_cell(ens_pr, None, None, include_ci=False)
            roc_str = _metric_cell(ens_roc, None, None, include_ci=False)
            f1_str = _metric_cell(ens_f1, None, None, include_ci=False)
            recall_str = _metric_cell(
                ens_recall, None, None, include_ci=False, as_percent=True,
            )
            if ember:
                ember_str = (
                    f"PR {_delta(ens_pr, ember.get('pr_auc'))} / "
                    f"ROC {_delta(ens_roc, ember.get('roc_auc'))}"
                )
            else:
                ember_str = "—"
        balance = f"{_int(n_mal)} / {_int(n_ben)}"
        ft_cell = f"[`{ft}`](filetypes/{ft}/README.md)" if link_routes else f"`{ft}`"
        lines.append(
            f"| {ft_cell} | {balance} | {pr_str} | {roc_str} | {f1_str} | {recall_str} | {ember_str} |"
        )
    return lines


def _three_way_table(metrics: dict[str, Any], filetypes: tuple[str, ...]) -> list[str]:
    """Three-way table: general (all-corpus), specialist (route-only), ensemble.
    Used in ENSEMBLE_MODEL.md to make the routing benefit explicit."""
    lines = [
        "| File type | Files | General ROC | Specialist ROC | Ensemble ROC | "
        "Strategy | Routing policy |",
        "|---|---:|---:|---:|---:|---|---|",
    ]
    for ft in filetypes:
        entry = metrics.get("filetypes", {}).get(ft)
        if not entry:
            continue
        g = entry.get("general", {})
        s = entry.get("specialist", {})
        e = entry.get("ensemble", {})
        strategy = entry.get("ensemble_strategy", "—")
        lines.append(
            f"| `{ft}` | {_int(entry.get('n_files'))} | "
            f"{_num(g.get('roc_auc'), 6)} | "
            f"{_num(s.get('roc_auc'), 6)} | "
            f"{_num(e.get('roc_auc'), 6)} | "
            f"`{strategy}` | "
            f"`{entry.get('ensemble_policy', '—')}` |"
        )
    return lines


def _generalist_table(metrics: dict[str, Any], filetypes: tuple[str, ...]) -> list[str]:
    """General-only per-filetype table for GENERALIST_MODEL.md, with EMBER's
    'All files → X' deltas where applicable."""
    lines = [
        "| File type | Files | ROC AUC | PR AUC | F1 | EMBER ROC (All files → X) | Δ ROC | EMBER PR | Δ PR |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    # First row: aggregate "all files"
    all_g = metrics.get("all_files", {}).get("general") or {}
    all_n = metrics.get("all_files", {}).get("n_files", 0)
    ember = _ember_for("all_files", "general")
    ember_roc = f"{ember['roc_auc']:.4f}" if ember else "—"
    ember_pr = f"{ember['pr_auc']:.4f}" if ember else "—"
    d_roc = _delta(all_g.get("roc_auc"), ember.get("roc_auc") if ember else None)
    d_pr = _delta(all_g.get("pr_auc"), ember.get("pr_auc") if ember else None)
    lines.append(
        f"| **all files** | {all_n} | "
        f"{_num(all_g.get('roc_auc'), 6)} | "
        f"{_num(all_g.get('pr_auc'), 6)} | "
        f"{_num(all_g.get('f1'), 4)} | "
        f"{ember_roc} | {d_roc} | {ember_pr} | {d_pr} |"
    )
    for ft in filetypes:
        entry = metrics.get("filetypes", {}).get(ft)
        if not entry:
            continue
        g = entry.get("general", {})
        ember = _ember_for(ft, "general")
        ember_roc = f"{ember['roc_auc']:.4f}" if ember else "—"
        ember_pr = f"{ember['pr_auc']:.4f}" if ember else "—"
        d_roc = _delta(g.get("roc_auc"), ember.get("roc_auc") if ember else None)
        d_pr = _delta(g.get("pr_auc"), ember.get("pr_auc") if ember else None)
        lines.append(
            f"| `{ft}` | {_int(entry.get('n_files'))} | "
            f"{_num(g.get('roc_auc'), 6)} | "
            f"{_num(g.get('pr_auc'), 6)} | "
            f"{_num(g.get('f1'), 4)} | "
            f"{ember_roc} | {d_roc} | {ember_pr} | {d_pr} |"
        )
    return lines


def _route_summary(config: dict[str, Any]) -> str:
    counts = {"general": 0, "filegroup": 0, "filetype": 0}
    for model in config.get("models", []):
        kind = model.get("kind")
        if kind in counts:
            counts[kind] += 1
    return (
        f"{counts['general']} general, "
        f"{counts['filegroup']} filegroup, "
        f"{counts['filetype']} filetype"
    )


def _level_table(levels: list[dict[str, Any]]) -> str:
    lines = [
        "| L | H target/1M | H recall | H FP/1M | H threshold | "
        "S target/1M | S recall | S FP/1M | S threshold |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for row in sorted(levels, key=lambda item: int(item["level"])):
        hostile = row["hostile"]
        suspicious = row["suspicious"]
        targets = row.get("targets") or {}
        hostile_target = (
            hostile.get("target_per_million")
            or hostile.get("target_fp_per_million")
            or targets.get("hostile_per_million")
        )
        suspicious_target = (
            suspicious.get("target_per_million")
            or suspicious.get("target_fp_per_million")
            or targets.get("suspicious_per_million")
        )
        h_threshold = hostile.get("threshold")
        s_threshold = suspicious.get("threshold")
        if h_threshold is None and isinstance(hostile.get("thresholds"), dict):
            h_threshold = "routed"
        if s_threshold is None and isinstance(suspicious.get("thresholds"), dict):
            s_threshold = "routed"
        lines.append(
            "| "
            f"{row['level']} | "
            f"{_num(hostile_target, 1)} | "
            f"{_pct(hostile.get('recall'))} | "
            f"{_num(hostile.get('fp_per_million'), 2)} | "
            f"{_num(h_threshold) if h_threshold != 'routed' else 'routed'} | "
            f"{_num(suspicious_target, 1)} | "
            f"{_pct(suspicious.get('recall'))} | "
            f"{_num(suspicious.get('fp_per_million'), 2)} | "
            f"{_num(s_threshold) if s_threshold != 'routed' else 'routed'} |"
        )
    return "\n".join(lines)


def _policy_levels(root: Path, route_name: str) -> list[str]:
    path = root / "route_policies.json"
    if not path.exists():
        return []
    with open(path) as f:
        policies = json.load(f)
    route = policies.get("routes", {}).get(route_name)
    if not route:
        return []
    lines = [
        "| L | Severity | Policy | Recall | FP | FP/1M | Thresholds |",
        "| ---: | --- | --- | ---: | ---: | ---: | --- |",
    ]
    for level_no in (5, 9):
        level = next((item for item in route.get("levels", []) if int(item["level"]) == level_no), None)
        if not level:
            continue
        for severity in ("hostile", "suspicious"):
            best = level[severity]["best"]
            lines.append(
                "| "
                f"{level_no} | {severity} | {best['policy']} | "
                f"{_pct(best.get('recall'))} | {_int(best.get('fp'))} | "
                f"{_num(best.get('fp_per_million'), 2)} | "
                f"`{json.dumps(best.get('thresholds', {}), sort_keys=True)}` |"
            )
    return lines


def _global_policy_table(root: Path) -> str:
    # Prefer test_metrics.json (honest evaluation on the locked test
    # partition) over global_policy_metrics.json (which after the dev/test
    # methodology is dev-derived). Fall back to dev metrics if test
    # evaluation hasn't been run on this bundle yet.
    test_path = root / "test_metrics.json"
    dev_path = root / "global_policy_metrics.json"
    if test_path.exists():
        path = test_path
    elif dev_path.exists():
        path = dev_path
    else:
        return ""
    with open(path) as f:
        data = json.load(f)
    total = data.get("rows") or 0
    # CP 95% upper bound on the test-observed FP rate per (level, severity).
    # This is the honest deployment-FP/M claim: "given x test FPs in N test
    # benigns, the true rate is ≤ this with 95% confidence." For
    # below-resolution rows, this column will exceed the L target — making
    # the volume floor visible in the table without footnote-only treatment.
    n_test_benign = int(data.get("benign") or 0)
    any_below = any(
        bool(lvl.get(sev, {}).get("below_resolution"))
        for lvl in data["levels"] for sev in ("hostile", "suspicious")
    )

    def _cp_upper(fp: int | None) -> float | None:
        if fp is None or n_test_benign <= 0:
            return None
        return _clopper_pearson_fp_per_million_upper(int(fp), n_test_benign, alpha=0.05)

    lines = [
        "| L | H target/1M | H recall | H FP/1M | H 95% CI upper | S target/1M | S recall | S FP/1M | S 95% CI upper |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for level_no in sorted(int(item["level"]) for item in data["levels"]):
        level = next(item for item in data["levels"] if int(item["level"]) == level_no)
        h = level["hostile"]
        s = level["suspicious"]
        h_target = _num(h.get("target_per_million"), 1)
        s_target = _num(s.get("target_per_million"), 1)
        if h.get("below_resolution"):
            h_target = h_target + "†"
        if s.get("below_resolution"):
            s_target = s_target + "†"
        h_cp = _cp_upper(h.get("fp"))
        s_cp = _cp_upper(s.get("fp"))
        lines.append(
            "| "
            f"{level_no} | {h_target} | "
            f"{_pct(h.get('recall'))} | {_num(h.get('fp_per_million'), 2)} | {_num(h_cp, 2)} | "
            f"{s_target} | "
            f"{_pct(s.get('recall'))} | {_num(s.get('fp_per_million'), 2)} | {_num(s_cp, 2)} |"
        )
    out = "\n".join(lines)
    out += (
        f"\n\n*95% CI upper* is the Clopper-Pearson upper bound on the deployment "
        f"FP rate given the observed FP count in {n_test_benign:,} test-partition "
        f"benigns. The honest deployment-FP/M claim sits below this number with "
        f"95% confidence."
    )
    if any_below:
        out += (
            "\n\n† below data resolution: the dev calibration sample is too small "
            "to credibly assert FP/M ≤ target at this level (95% CI). The deployed "
            "threshold falls back to the loosest empirical 0-FP fit; the FP/M and "
            "95% CI columns show what the test partition actually achieves under "
            "that threshold, which exceeds the L target."
        )
    return out


def _model_algo(config: dict[str, Any] | None) -> str:
    if not config:
        return "LightGBM binary classifier (`azoth`)."
    return (
        "LightGBM binary classifier: "
        f"estimators={config.get('n_estimators', '?')}, "
        f"num_leaves={config.get('num_leaves', '?')}, "
        f"max_depth={config.get('max_depth', '?')}, "
        f"min_child_samples={config.get('min_child_samples', '?')}, "
        f"learning_rate={config.get('learning_rate', '?')}, "
        f"subsample={config.get('subsample', '?')}, "
        f"colsample={config.get('colsample_bytree', '?')}, "
        f"reg_alpha={config.get('reg_alpha', '?')}, "
        f"reg_lambda={config.get('reg_lambda', '?')}, "
        f"early_stop={config.get('early_stopping_rounds', '?')}, "
        f"device={config.get('device', 'cpu')}."
    )


def _feature_summary() -> str:
    items = sorted([
        "aggregate finding counts",
        "ATT&CK/MBC n-grams",
        "cleave trait taxonomy",
        "element tokens",
        "extended file metrics",
        "format-group hints",
        "hopper score",
        "hostile density/escalation",
        "packaged capability mode=paths",
        "path/criticality bigrams/trigrams",
        "repetition penalties",
        "severity distribution",
        "soft presence",
        "structural coverage",
    ], key=str.casefold)
    return "\n".join(f"  - {item}" for item in items)


def _general_evaluation(root: Path) -> dict[str, Any]:
    eval_path = root / "general" / "evaluation.json"
    if not eval_path.exists():
        return {}
    with open(eval_path) as f:
        return json.load(f)


def _general_train_config(root: Path) -> dict[str, Any] | None:
    experiment = _general_evaluation(root).get("experiment") or {}
    config = experiment.get("train_config")
    if isinstance(config, dict):
        return config
    # Fallback: parse the LightGBM dump for its embedded config block.
    # For multi-seed bundles, any seed's config is identical (same
    # hyperparameters); pick the deterministic primary.
    try:
        return _lightgbm_model_config(bundle.primary_model_file(root / "general"))
    except FileNotFoundError:
        return None


def _lightgbm_model_config(path: Path) -> dict[str, Any] | None:
    if not path.exists():
        return None
    key_map = {
        "num_iterations": "n_estimators",
        "num_leaves": "num_leaves",
        "max_depth": "max_depth",
        "min_data_in_leaf": "min_child_samples",
        "learning_rate": "learning_rate",
        "bagging_fraction": "subsample",
        "feature_fraction": "colsample_bytree",
        "lambda_l1": "reg_alpha",
        "lambda_l2": "reg_lambda",
    }
    out: dict[str, Any] = {"device": "cpu"}
    with open(path, errors="ignore") as f:
        for line in f:
            if not line.startswith("[") or ": " not in line:
                continue
            raw_key, raw_value = line.strip()[1:-1].split(": ", 1)
            key = key_map.get(raw_key)
            if key is None:
                continue
            try:
                numeric = float(raw_value)
            except ValueError:
                continue
            out[key] = int(numeric) if numeric.is_integer() else numeric
    return out or None


def _feature_count(path: Path, fallback: Any = None) -> Any:
    if path.exists():
        with open(path) as f:
            spec = json.load(f)
        return spec.get("total_features") or len(spec.get("feature_names", []))
    return fallback


def _write(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n")


def _write_general(root: Path) -> None:
    tuning_path = root / "general" / "threshold_tuning.json"
    with open(tuning_path) as f:
        tuning = json.load(f)
    corpus = tuning.get("corpus", {})
    levels = tuning["severity_levels"]
    evaluation = _general_evaluation(root)
    train_config = _general_train_config(root)
    lines = [
        "# Azoth General",
        "",
        "General malware detector used for every routed decision.",
        "",
        f"- Inputs: shared `feature_spec.json` "
        f"({_int(_feature_count(root / 'general' / 'feature_spec.json', evaluation.get('n_features')))} features) "
        "extracted from cleave reports.",
        "- Feature families:",
        _feature_summary(),
        f"- Technique: {_model_algo(train_config)}",
        f"- Calibration corpus: {_int(corpus.get('samples'))} rows "
        f"({_int(corpus.get('malware'))} malware, {_int(corpus.get('benign'))} benign).",
        "",
        _level_table(levels),
    ]
    _write(root / "general" / "README.md", "\n".join(lines))


def _write_route(root: Path, path: Path) -> None:
    """Per-route README. ≤50-line budget: one metrics table + a compact
    training profile + a single line on routing policy. Detailed L0..L20
    operating points and full ensemble explanations live in the bundle's
    top-level cards, not here."""
    with open(path / "benchmark.json") as f:
        data = json.load(f)
    metrics = data.get("metrics") or {}
    name = data["name"]
    kind = data["kind"]
    file_types = ", ".join(f"`{item}`" for item in data.get("file_types", []))

    per_ft = _load_per_filetype_metrics(root)
    pf_entry = per_ft.get("filetypes", {}).get(name) if kind == "filetype" else None
    spec_metrics = (pf_entry or {}).get("specialist") or {}
    ember = _ember_for(name, "specialist") if kind == "filetype" else None
    allowed_routes = (pf_entry or {}).get("ensemble_allowed_routes") or []

    lines = [
        f"# `{kind}/{name}`",
        "",
        f"LightGBM specialist for {file_types}. Member of the Azoth routed "
        f"ensemble; bundle root: [../..](../..).",
        "",
    ]

    if metrics.get("roc_auc") is not None and float(metrics["roc_auc"]) <= 0.501:
        lines.extend([
            "> Benchmark AUC degenerate on this split. Routed full-corpus calibration governs deployment.",
            "",
        ])

    if pf_entry:
        n_eval = pf_entry.get("n_files", 0)
        n_mal = pf_entry.get("n_malware")
        n_ben = pf_entry.get("n_benign")
        ens_metrics = pf_entry.get("ensemble") or {}
        ember_str = (
            f"PR {_delta(spec_metrics.get('pr_auc'), ember.get('pr_auc'))} / "
            f"ROC {_delta(spec_metrics.get('roc_auc'), ember.get('roc_auc'))}"
            if ember
            else "—"
        )
        # Lead with the routed ensemble's model properties — PR AUC,
        # ROC AUC, F1, recall@3FP/M — on this filetype's slice of the
        # locked test partition. These describe what the model's scores
        # rank; how litmus thresholds them at each severity level is
        # documented in route_policies.md.
        lines.extend([
            "## Ensemble Performance",
            "",
            f"Routed ensemble (general + filegroup + filetype where applicable) "
            f"on the `{name}` slice of the locked test partition: "
            f"{_int(n_mal)} malware / {_int(n_ben)} benign ({_int(n_eval)} rows).",
            "",
            "| PR AUC | ROC AUC | F1 | Recall @ 3FP/M | Brier |",
            "|---:|---:|---:|---:|---:|",
            (
                f"| {_metric_cell(ens_metrics.get('pr_auc'), None, None, include_ci=False)} | "
                f"{_metric_cell(ens_metrics.get('roc_auc'), None, None, include_ci=False)} | "
                f"{_metric_cell(ens_metrics.get('f1'), None, None, include_ci=False)} | "
                f"{_metric_cell(ens_metrics.get('recall_at_3fp_per_million'), None, None, include_ci=False, as_percent=True)} | "
                f"{_num(ens_metrics.get('brier'), 4)} |"
            ),
            "",
        ])
        # Then the specialist alone, for diagnosing the route's
        # standalone contribution.
        lines.extend([
            f"## Specialist Performance",
            "",
            f"`filetypes/{name}` specialist scored *alone* on the same slice "
            f"(the ensemble usually does better — that's the point of the "
            f"routing).",
            "",
            "| PR AUC | ROC AUC | F1 | Recall @ 3FP/M | Brier | Δ vs EMBER 2024 |",
            "|---:|---:|---:|---:|---:|---:|",
            (
                f"| {_metric_cell(spec_metrics.get('pr_auc'), None, None, include_ci=False)} | "
                f"{_metric_cell(spec_metrics.get('roc_auc'), None, None, include_ci=False)} | "
                f"{_metric_cell(spec_metrics.get('f1'), None, None, include_ci=False)} | "
                f"{_metric_cell(spec_metrics.get('recall_at_3fp_per_million'), None, None, include_ci=False, as_percent=True)} | "
                f"{_num(spec_metrics.get('brier'), 4)} | {ember_str} |"
            ),
            "",
        ])
    else:
        lines.extend([
            f"## Performance",
            "",
            f"Training-time benchmark only (no test-partition rows for `{name}`). "
            f"ROC {_num(metrics.get('roc_auc'), 6)}, "
            f"PR {_num(metrics.get('avg_precision'), 6)}, "
            f"F1 {_num(metrics.get('max_f1'), 4)} on "
            f"{_int(data.get('benchmark_rows'))} rows "
            f"({_int(data.get('benchmark_malware'))} mal / "
            f"{_int(data.get('benchmark_benign'))} ben).",
            "",
        ])

    routes_str = ", ".join(f"`{r}`" for r in allowed_routes) if allowed_routes else "none"
    lines.extend([
        "## Routing",
        "",
        f"Files matching `{name}` are scored by {routes_str}. The ensemble's "
        "per-row score is whatever combiner strategy "
        f"(`{pf_entry.get('ensemble_strategy', '—') if pf_entry else '—'}`) "
        "the metrics step selected for this route. The per-level operating "
        "thresholds litmus applies on top live in "
        f"[`route_policies.md`](../../route_policies.md).",
        "",
        "## Training",
        "",
    ])
    cfg = data.get("train_config") or {}
    n_features = data.get("n_features", "?")
    spec_policy = data.get("feature_spec_policy", "?")
    lines.extend([
        "| Parameter | Value |",
        "|---|---:|",
        f"| Algorithm | LightGBM binary classifier |",
        f"| Train rows | {_int(data.get('train_rows'))} "
        f"({_int(data.get('train_malware'))} mal / {_int(data.get('train_benign'))} ben) |",
        f"| Feature spec | {n_features} features (`{spec_policy}`) |",
        f"| n_estimators | {cfg.get('n_estimators', '?')} |",
        f"| num_leaves | {cfg.get('num_leaves', '?')} |",
        f"| max_depth | {cfg.get('max_depth', '?')} |",
        f"| min_child_samples | {cfg.get('min_child_samples', '?')} |",
        f"| learning_rate | {cfg.get('learning_rate', '?')} |",
        f"| subsample / colsample | {cfg.get('subsample', '?')} / {cfg.get('colsample_bytree', '?')} |",
        f"| reg_alpha / reg_lambda | {cfg.get('reg_alpha', '?')} / {cfg.get('reg_lambda', '?')} |",
        f"| early_stopping_rounds | {cfg.get('early_stopping_rounds', '?')} |",
        f"| device | {cfg.get('device', 'cpu')} |",
    ])
    _write(path / "README.md", "\n".join(line for line in lines if line is not None) + "\n")


def _write_bundle(root: Path) -> None:
    """Bundle README. Lead paragraph, performance table (linked to per-route
    cards), operating points, provenance, limits, sources. No imperatives,
    no marketing, no "see also". Pike voice."""
    with open(root / "config.json") as f:
        config = json.load(f)
    metrics = _load_per_filetype_metrics(root)
    eval_data = _load_deployed_eval(root)
    n_eval = eval_data.get("rows") or metrics.get("n_rows_evaluated", 0)
    fit_rows = _int(config.get("fit_rows") or config.get("rows"))
    fit_part = config.get("fit_partition") or "dev"
    n_filetype = sum(
        1 for m in (config.get("models") or [])
        if str(m.get("route") or "").startswith("filetypes/")
    )
    n_filegroup = sum(
        1 for m in (config.get("models") or [])
        if str(m.get("route") or "").startswith("filegroups/")
    )
    lines = [
        "# Azoth",
        "",
        "Static malware detection by routed ensemble. A general LightGBM "
        "model scores every file. Per-filetype specialists score files "
        f"in their domain — PE, ELF, JavaScript, PDF, and {n_filetype - 4} "
        "more. A file is flagged when any route's score crosses its "
        "calibrated threshold.",
        "",
        "The point of routing is that the evidence differs by format. A "
        "PE's section table is signal. A PDF's stream dictionary is "
        "signal. A shell script's token distribution is signal. One "
        "generalist trained over all of them learns averages; a "
        "specialist trained on one of them learns the format.",
        "",
        f"Thresholds and isotonic calibrators were fit on a {fit_rows}-row "
        f"{fit_part} partition (12.5% of the labeled corpus). The "
        f"numbers in this README come from a locked {_int(n_eval)}-row "
        "test partition, disjoint from training and calibration. The "
        "bundle is loaded at scan time by "
        "[litmus](https://codeberg.org/atomdrift/litmus). EMBER 2024 "
        "reference: Joyce et al., *KDD'25*.",
        "",
        "## Use",
        "",
        "Input is a JSON report produced by `cleave`. Output is one "
        "verdict — `benign`, `suspicious`, or `hostile` — qualified by a "
        "severity level L0..L20. Litmus reads the hostile and suspicious "
        "thresholds at the same level; the deployed default is L3. Lower "
        "levels tighten the operating point; higher levels loosen it.",
        "",
        "## Bundle layout",
        "",
        "`config.json` records the deployed thresholds. Each route lives "
        f"in its own subdirectory: `general/`, one of {n_filegroup} "
        f"`filegroups/<name>/`, or one of {n_filetype} "
        "`filetypes/<name>/`. A route directory carries three files: "
        "`model.txt` (LightGBM), `feature_spec.json` (the features the "
        "model expects), and `calibrator.json` (isotonic probability "
        "calibrator).",
        "",
        "Further reading: [DESIGN.md](DESIGN.md) for architecture and "
        "FP-budget design, [ENSEMBLE_MODEL.md](ENSEMBLE_MODEL.md) for "
        "routing details, [GENERALIST_MODEL.md](GENERALIST_MODEL.md) for "
        "the single-model baseline. License: Apache 2.0.",
        "",
        "## Per-filetype Ensemble Performance",
        "",
        "Each row is the routed ensemble's intrinsic ranking quality on "
        "that filetype's slice of the locked test partition — PR AUC, "
        "ROC AUC, F1 at the F-beta-tuned threshold, and recall at a "
        "3 FP/M operating point. These are properties of the model's "
        "scores; how litmus chooses to threshold those scores at each "
        "severity level is a runtime concern documented in "
        "[`route_policies.md`](route_policies.md).",
        "",
        "A filetype appears here when it has at least 25 malware and "
        "25 benign in the test slice, or at least 100 of each across "
        "the full labeled corpus. Pure archive wrappers (zip, tar, "
        "gz, …), `data`, and `unknown` are excluded — their score "
        "reflects the container's shape, not the classifier's quality.",
        "",
        "**Optimization target.** Each filetype's ensemble combiner is "
        "selected to maximize **recall at 3 FP/M** on the dev partition, "
        "with PR AUC as a tiebreak. Selection is constrained so the "
        "ensemble can never report worse than the specialist alone — "
        "when no combiner clears the specialist on dev, the ensemble "
        "falls back to `specialist_priority` (which equals the "
        "specialist by construction). This matches the deployment "
        "budget litmus operates at and the design intent that routing "
        "must improve, not degrade, the per-filetype model.",
        "",
        *_ensemble_table(
            metrics, eval_data, _headline_filetypes(metrics, config, eval_data),
            link_routes=True,
        ),
        "",
        "PR AUC summarizes recall against precision across operating "
        "points. Recall@3FP/M is the deployment-budget headline; for "
        "filetypes whose dev slice cannot resolve 3 FP/M empirically "
        "it is GPD-tail-extrapolated. EMBER 2024 deltas are reported "
        "where Joyce et al. publish per-filetype numbers (Table 5, "
        "All files → X).",
        "",
        "## Provenance",
        "",
        f"Calibration snapshot `{config.get('calibration_snapshot_id')}`, "
        f"score-table `{_short_hash(config.get('score_table_hash'))}`, "
        f"model-set `{_short_hash(config.get('model_set_hash'))}`. "
        f"{_route_summary(config)} routes.",
        "",
        "## Limits",
        "",
        "- Strict L0..L3 FP/M targets sit below empirical resolution on a single dev partition (one FP per 150k benigns ≈ 6 FP/M); their thresholds are GPD tail-extrapolations.",
        "- The split is content-deduplicated by `canonical_sha256`, not family-aware. Campaign-level generalization may be overstated.",
        "- Deployment distribution may differ from the training corpus.",
        "",
        "## Sources",
        "",
        "[MalwareBazaar](https://bazaar.abuse.ch/), "
        "[VirusShare](https://virusshare.com/), "
        "[Backstabber's Knife Collection](https://dasfreak.github.io/Backstabbers-Knife-Collection/), "
        "[DataDog malicious-software-packages-dataset](https://github.com/DataDog/malicious-software-packages-dataset), "
        "[VX Underground](https://vx-underground.org/), "
        "[PyPI MalRegistry](https://github.com/lxyeternal/pypi_malregistry), "
        "[Linux Malware Samples](https://github.com/MalwareSamples/Linux-Malware-Samples), "
        "[Tim (Wadhwa-)Brown's Linux Malware Repo](https://github.com/timb-machine/linux-malware), "
        "[Javascript Malware Collection](https://github.com/HynekPetrak/javascript-malware-collection), "
        "[ObjectiveSee macOS Malware Collection](https://github.com/objective-see/Malware), "
        "[Practical Security Analytics PE Malware ML Dataset](https://practicalsecurityanalytics.com/pe-malware-machine-learning-dataset/), "
        "[Ultimate RAT Collection](https://github.com/Cryakl/Ultimate-RAT-Collection).",
    ]
    _write(root / "README.md", "\n".join(lines) + "\n")


def _write_ensemble_card(root: Path) -> None:
    """ENSEMBLE_MODEL.md — explains how routing works and what policy
    forms can fire. The bundle README has the per-filetype numbers."""
    lines = [
        "# Azoth — Routed Ensemble",
        "",
        "## How a file is scored",
        "",
        "1. `cleave` identifies the file's format — `elf`, `pe`, `pdf`, "
        "`javascript`, and so on.",
        "2. `route_policies.json` answers: given that format and a "
        "severity level L0..L20, which routes are allowed, and at what "
        "calibrated thresholds?",
        "3. Each allowed route scores the file with its own model and "
        "feature spec.",
        "4. If any allowed route's score crosses its threshold, the "
        "file is flagged at that severity.",
        "",
        "A route is one of: the general model, a filegroup specialist "
        "(`filegroups/<name>`), or a filetype specialist "
        "(`filetypes/<name>`). Specialists are trained only on files of "
        "their domain; the general model is trained on everything.",
        "",
        "## Per-filetype combiner selection",
        "",
        "The Ensemble Performance row in the bundle README shows the "
        "**best combiner per filetype**, picked from a handful of "
        "candidates evaluated on the dev partition:",
        "",
        "- `specialist_priority` — for each row, use the most specific "
        "route's raw score (filetype specialist → filegroup → general). "
        "By construction this equals the specialist on filetype-X rows, "
        "so `ensemble ≥ specialist` holds always for this strategy.",
        "- `calibrated_max` — per-route isotonic-calibrate (5-fold OOF), "
        "then `max` of the calibrated probabilities. Wins when routes "
        "score on different distributions and the calibrated max is "
        "more comparable than the raw max.",
        "- `stacked_lr` / `stacked_xgb` — a small stacker (logistic "
        "regression or XGBoost) over the per-route calibrated probs. "
        "Wins when routes carry complementary signal that linear/tree "
        "combination can exploit.",
        "- `naive_max` — raw `max` across routes, kept as a sanity "
        "check; rejected from the picker because raw scores don't share "
        "a probability calibration.",
        "",
        "**Selection criterion**: maximize **recall at 3 FP/M** on the "
        "dev partition (matching the deployment FP/M target), with "
        "**PR AUC** as a secondary tiebreak. The picker is constrained "
        "by a floor: no combiner may report worse than "
        "`specialist_priority`, on either dev or test. If a combiner "
        "would clear the floor on dev but regress below it on test "
        "(sampling variance), the report falls back to "
        "`specialist_priority`. This guarantees the **ensemble ≥ "
        "specialist** invariant in every row of the bundle README.",
        "",
        "## Routing policies",
        "",
        "Per filetype per level, `azoth_route_policy_search.py` picks "
        "one of these policy forms by recall at the FP/M target, with "
        "F1 and fp-count tiebreaks. The chosen policy and its "
        "calibrated thresholds are written to `route_policies.json` "
        "and read by litmus at scan time:",
        "",
        "- `joint_or_at_fp_N` — OR-rule across the allowed routes, "
        "with per-route thresholds calibrated to a joint FP/M target "
        "of N per million. The common case.",
        "- `learned_blend_at_fp_N` — a logit blend "
        "`σ(b + Σ wᵢ · logit(pᵢ))` over calibrated route probabilities, "
        "thresholded to hit the FP/M target. Wins when route scores "
        "are complementary in a way a simple OR misses.",
        "- `filetype_only` / `filetype_only_at_fp_N` — the specialist "
        "fires alone.",
        "- `general_only`, `group_only`, `or_general_primary`, "
        "`group_primary_with_escape` — the single-route or "
        "single-primary variants.",
        "- `calibrate_inherited` — the level inherits its threshold "
        "from a stricter level (no fresh calibration was warranted).",
        "- `no_policy` — no configuration meets the FP/M target at this "
        "level; the route does not fire at this severity.",
        "",
        "## Severity levels (L0..L20)",
        "",
        "L0..L20 are observation-derived strictness grades, not "
        "optimization targets. For each route, level Lk's threshold is "
        "set so that roughly qk benigns per million would be flagged "
        "on the dev partition. Strict levels (where `n_benign · qk · "
        "10⁻⁶ < 1` falls below empirical resolution) use a generalized "
        "Pareto fit to the benign-score upper tail; looser levels use "
        "direct empirical quantiles.",
        "",
        "Litmus reads the per-level thresholds from "
        "`route_policies.json` and assigns severity per file.",
        "",
        "Default deploy level: L3 (litmus loads both hostile and "
        "suspicious thresholds at the same level). Per-route L0..L20 "
        "thresholds and observed FP/M live in "
        "[route_policies.md](route_policies.md) and each "
        "`filetypes/<name>/README.md`.",
    ]
    _write(root / "ENSEMBLE_MODEL.md", "\n".join(lines))


def _write_generalist_card(root: Path) -> None:
    """GENERALIST_MODEL.md — single-model card for the general classifier.
    Reference numbers; the deployed product is the ensemble (see ENSEMBLE_MODEL.md)."""
    with open(root / "config.json") as f:
        config = json.load(f)
    metrics = _load_per_filetype_metrics(root)
    eval_data = _load_deployed_eval(root)
    train_config = _general_train_config(root)
    evaluation = _general_evaluation(root)
    eval_metrics = evaluation.get("metrics") or {}
    feature_spec_path = root / "general" / "feature_spec.json"
    n_features = _feature_count(feature_spec_path, evaluation.get("n_features"))
    headline = _headline_filetypes(metrics, config, eval_data)
    lines = [
        "# Azoth — Generalist Model",
        "",
        "One LightGBM classifier trained on the entire labeled corpus, "
        "every supported filetype mixed together. The point of "
        "having a generalist is that some files don't fit any "
        "specialist's domain, and a single model across all of them "
        "establishes a floor.",
        "",
        "The generalist alone is not what gets deployed. It is one "
        "route in the ensemble — see "
        "[ENSEMBLE_MODEL.md](ENSEMBLE_MODEL.md). The numbers here "
        "are reported for transparency, and to line up directly "
        "against the \"All files\" row in EMBER 2024 (Joyce et al., "
        "*KDD'25*, Table 5).",
        "",
        "## Per-filetype performance",
        "",
        "Generalist model scored on each filetype's slice of the "
        "locked test partition (12.5% holdout, SHA256-deterministic, "
        "disjoint from training and dev calibration). EMBER columns "
        "reference Joyce et al.'s \"All files → X\" rows where they "
        "exist.",
        "",
        *_generalist_table(metrics, headline),
        "",
        "## Training",
        "",
        f"- Algorithm: {_model_algo(train_config)}",
        f"- Feature spec: `general/feature_spec.json` "
        f"({_int(n_features)} features)",
        "- Split: 75% train / 12.5% dev / 12.5% test, "
        "SHA256-deterministic. The model is fit on train. Calibrators "
        "and L0..L20 thresholds are fit on dev. The numbers above "
        "come from test.",
        "",
        "## Training-time evaluation",
        "",
        "The training pipeline reports metrics on a hard-pool holdout — "
        "a curated subset of train, used for early stopping and "
        "hyperparameter selection. These numbers run hot because the "
        "pool is selected for difficulty during training, not after. "
        "The per-filetype table above is the better reference for "
        "production expectations.",
        "",
        f"- Accuracy: {_pct(eval_metrics.get('accuracy'))}",
        f"- F1: {_num(eval_metrics.get('f1'), 4)}",
        f"- ROC AUC: {_num(eval_metrics.get('roc_auc'), 6)}",
        f"- Average Precision: {_num(eval_metrics.get('avg_precision'), 6)}",
        f"- Brier: {_num(eval_metrics.get('brier'), 4)}",
    ]
    _write(root / "GENERALIST_MODEL.md", "\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--azoth-root", type=Path, default=Path("out/models/azoth"))
    args = parser.parse_args()
    root = args.azoth_root
    _write_bundle(root)
    _write_ensemble_card(root)
    _write_generalist_card(root)
    _write_general(root)
    for parent in (root / "filegroups", root / "filetypes"):
        if not parent.exists():
            continue
        for child in sorted(item for item in parent.iterdir() if item.is_dir()):
            if (child / "benchmark.json").exists():
                _write_route(root, child)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
