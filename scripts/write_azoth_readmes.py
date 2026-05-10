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

from collimator import bundle  # noqa: E402  — late import after sys.path patch


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
    return "-" if value is None else str(int(value))


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
    """Format `ours - theirs` with sign (+ / -) for direct comparison."""
    if ours is None or theirs is None:
        return "-"
    try:
        d = float(ours) - float(theirs)
    except (TypeError, ValueError):
        return "-"
    if math.isnan(d):
        return "-"
    sign = "+" if d >= 0 else ""
    return f"{sign}{d:.4f}"


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


def _ensemble_table(metrics: dict[str, Any], filetypes: tuple[str, ...]) -> list[str]:
    """Headline table: routed ensemble per filetype, with EMBER 2024 delta where
    a published reference exists.  ROC + PR + F1 columns; n_files for context.

    The ensemble column is the *deployed* reality: when a route's policy at
    the headline operating level is `no_policy` (no allowed routes meet the
    FP/M target), the ensemble doesn't fire — we mark it explicitly rather
    than falling back to the specialist's standalone number, so the table
    reflects what production actually does on that filetype.
    """
    lines = [
        "| File type | Files | Routed ROC AUC | Routed PR AUC | Routed F1 | EMBER ROC | Δ ROC | EMBER PR | Δ PR |",
        "|---|---:|---:|---:|---:|---:|---:|---:|---:|",
    ]
    for ft in filetypes:
        entry = metrics.get("filetypes", {}).get(ft)
        if not entry:
            continue
        ens = entry.get("ensemble") or {}
        policy = entry.get("ensemble_policy")
        ember = _ember_for(ft, "specialist")
        ember_roc = f"{ember['roc_auc']:.4f}" if ember else "—"
        ember_pr = f"{ember['pr_auc']:.4f}" if ember else "—"
        ens_roc = ens.get("roc_auc")
        ens_pr = ens.get("pr_auc")
        ens_f1 = ens.get("f1")
        # Headline columns are raw discrimination metrics (AUC/PR AUC/F1) — the
        # combiner's continuous-domain ranking ability.  These are EMBER-comparable
        # by design.  The deployed thresholded gate (L=N policy) is a separate
        # operational concern surfaced on the per-route cards, not here.
        if ens_roc is None or ens.get("n_evaluated", 1) == 0:
            roc_str = "—"
            pr_str = "—"
            f1_str = "—"
            d_roc = "—"
            d_pr = "—"
        else:
            roc_str = _num(ens_roc, 4)
            pr_str = _num(ens_pr, 4)
            f1_str = _num(ens_f1, 4)
            d_roc = _delta(ens_roc, ember.get("roc_auc") if ember else None)
            d_pr = _delta(ens_pr, ember.get("pr_auc") if ember else None)
        lines.append(
            f"| `{ft}` | {entry['n_files']} | "
            f"{roc_str} | {pr_str} | {f1_str} | "
            f"{ember_roc} | {d_roc} | {ember_pr} | {d_pr} |"
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
            f"| `{ft}` | {entry['n_files']} | "
            f"{_num(g.get('roc_auc'), 4)} | "
            f"{_num(s.get('roc_auc'), 4)} | "
            f"{_num(e.get('roc_auc'), 4)} | "
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
        f"{_num(all_g.get('roc_auc'), 4)} | "
        f"{_num(all_g.get('pr_auc'), 4)} | "
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
            f"| `{ft}` | {entry['n_files']} | "
            f"{_num(g.get('roc_auc'), 4)} | "
            f"{_num(g.get('pr_auc'), 4)} | "
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
    lines = [
        "| L | H target/1M | H accuracy | H recall | H FP/1M | S target/1M | S accuracy | S recall | S FP/1M |",
        "| ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    for level_no in range(10):
        level = next(item for item in data["levels"] if int(item["level"]) == level_no)
        h = level["hostile"]
        s = level["suspicious"]
        h_accuracy = None
        s_accuracy = None
        if total:
            h_accuracy = ((h.get("tp") or 0) + (h.get("tn") or 0)) / total
            s_accuracy = ((s.get("tp") or 0) + (s.get("tn") or 0)) / total
        lines.append(
            "| "
            f"{level_no} | {_num(h.get('target_per_million'), 1)} | "
            f"{_pct(h_accuracy)} | {_pct(h.get('recall'))} | {_num(h.get('fp_per_million'), 2)} | "
            f"{_num(s.get('target_per_million'), 1)} | "
            f"{_pct(s_accuracy)} | {_pct(s.get('recall'))} | {_num(s.get('fp_per_million'), 2)} |"
        )
    return "\n".join(lines)


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
    """Per-route README. Leads with the specialist's single-model performance
    on the test bucket (apples-to-apples vs EMBER 2024 where applicable),
    states how the routed ensemble uses this specialist, then training
    profile, then operational FP/M policy levels at the bottom."""
    with open(path / "benchmark.json") as f:
        data = json.load(f)
    metrics = data.get("metrics") or {}
    name = data["name"]
    kind = data["kind"]
    file_types = ", ".join(f"`{item}`" for item in data.get("file_types", []))
    route_prefix = "filegroups" if kind == "filegroup" else "filetypes"

    # Pull the routed-ensemble per-filetype block for this route, if any.
    per_ft = _load_per_filetype_metrics(root)
    pf_entry = per_ft.get("filetypes", {}).get(name) if kind == "filetype" else None
    spec_metrics = (pf_entry or {}).get("specialist") or {}
    ens_metrics = (pf_entry or {}).get("ensemble") or {}
    ember = _ember_for(name, "specialist") if kind == "filetype" else None
    allowed_routes = (pf_entry or {}).get("ensemble_allowed_routes") or []
    ensemble_policy = (pf_entry or {}).get("ensemble_policy") or "—"

    warning = ""
    if metrics.get("roc_auc") is not None and float(metrics["roc_auc"]) <= 0.501:
        warning = (
            "\n> ⚠ Benchmark AUC is degenerate on this split — keep the artifact "
            "for coverage, but rely on routed full-corpus calibration before relying on it."
        )

    lines = [
        f"# Azoth {kind.title()} — `{name}`",
        "",
        f"Specialist classifier for {file_types}. Used by the routed ensemble — see [../../ENSEMBLE_MODEL.md](../../ENSEMBLE_MODEL.md).",
        "",
        warning if warning else "",
        "## Single-model performance",
        "",
    ]
    if pf_entry:
        n_eval = pf_entry.get("n_files", 0)
        ember_roc_str = f"{ember['roc_auc']:.4f}" if ember else "—"
        ember_pr_str = f"{ember['pr_auc']:.4f}" if ember else "—"
        ember_roc_val = ember.get("roc_auc") if ember else None
        ember_pr_val = ember.get("pr_auc") if ember else None
        lines.extend([
            f"On `{name}` test-partition rows (n={n_eval}, SHA256-deterministic 12.5% locked holdout):",
            "",
            "| Metric | Specialist (this model alone) | EMBER 2024 reference | Δ |",
            "|---|---:|---:|---:|",
            f"| ROC AUC | {_num(spec_metrics.get('roc_auc'), 4)} | {ember_roc_str} | "
            f"{_delta(spec_metrics.get('roc_auc'), ember_roc_val)} |",
            f"| PR AUC | {_num(spec_metrics.get('pr_auc'), 4)} | {ember_pr_str} | "
            f"{_delta(spec_metrics.get('pr_auc'), ember_pr_val)} |",
            f"| F1 | {_num(spec_metrics.get('f1'), 4)} | — | — |",
            f"| Brier (calibration) | {_num(spec_metrics.get('brier'), 4)} | — | — |",
            "",
        ])
    else:
        lines.extend([
            "Training-time benchmark (no test-bucket-only metric on file):",
            "",
            f"- ROC AUC / PR AUC / F1: {_num(metrics.get('roc_auc'), 4)} / "
            f"{_num(metrics.get('avg_precision'), 4)} / {_num(metrics.get('max_f1'), 4)}",
            f"- Benchmark rows: {_int(data.get('benchmark_rows'))} "
            f"({_int(data.get('benchmark_malware'))} malware, "
            f"{_int(data.get('benchmark_benign'))} benign).",
            "",
        ])

    if pf_entry:
        ens_block = [
            "## How the ensemble uses this specialist",
            "",
            f"At the default operating level, the deployed routing policy for `{name}` is `{ensemble_policy}`.",
        ]
        if allowed_routes:
            ens_block.append(
                f"Routes consulted (max-of-thresholds): {', '.join(f'`{r}`' for r in allowed_routes)}."
            )
        ens_block.extend([
            "",
            f"Ensemble's headline numbers on this filetype's test bucket: "
            f"ROC AUC = **{_num(ens_metrics.get('roc_auc'), 4)}**, "
            f"PR AUC = **{_num(ens_metrics.get('pr_auc'), 4)}**, "
            f"F1 = **{_num(ens_metrics.get('f1'), 4)}**. "
            "When the ensemble lags the specialist, the router is being conservative for FP/M-budget reasons; the specialist alone is what production would get if you bypassed routing.",
            "",
        ])
        lines.extend(ens_block)

    lines.extend([
        "## Training",
        "",
        f"- Inputs: shared general `feature_spec.json` ({data.get('n_features')} features); feature-spec policy `{data.get('feature_spec_policy')}`.",
        f"- Algorithm: {_model_algo(data.get('train_config'))}",
        "- Feature families:",
        _feature_summary(),
        f"- Training rows: {_int(data.get('train_rows'))} "
        f"({_int(data.get('train_malware'))} malware, {_int(data.get('train_benign'))} benign).",
        f"- Internal training-time benchmark rows: {_int(data.get('benchmark_rows'))} "
        f"({_int(data.get('benchmark_malware'))} malware, "
        f"{_int(data.get('benchmark_benign'))} benign).",
        f"- Internal training-time benchmark AUC/AP/F1: {_num(metrics.get('roc_auc'), 4)} / "
        f"{_num(metrics.get('avg_precision'), 4)} / {_num(metrics.get('max_f1'), 4)}.",
        "",
        "## Operational policy levels (advanced)",
        "",
        "Per-FP/M-target operating points for this specialist. Default deploy uses L3 hostile, L5 suspicious; lower levels = stricter FP budget. Useful when you need to tune deployed sensitivity.",
        "",
        _level_table(data["levels"]),
    ])
    policy_lines = _policy_levels(root, f"{route_prefix}/{name}")
    if policy_lines:
        lines.extend([
            "",
            "## Routed policy decisions",
            "",
            "What the ensemble actually does with this route at each operating level.",
            "",
            *policy_lines,
        ])
    _write(path / "README.md", "\n".join(line for line in lines if line is not None))


def _write_bundle(root: Path) -> None:
    """Write the top-level README — the front door for anyone evaluating the
    bundle.  Showcases the routed ensemble's per-filetype performance with
    EMBER 2024 deltas, and points at the deeper cards."""
    with open(root / "config.json") as f:
        config = json.load(f)
    metrics = _load_per_filetype_metrics(root)
    eval_note = (
        "test-partition only (apples-to-apples vs EMBER 2024 — locked holdout, never seen in training or calibration)"
        if metrics.get("evaluated_on") == "test_bucket_only"
        else "full corpus including training rows — re-run `compute_routed_metrics.py --db ...` for honest test-only numbers"
    )
    n_eval = metrics.get("n_rows_evaluated", 0)
    lines = [
        "# Azoth — Routed Multi-Format Malware Classifier",
        "",
        "Azoth is a **routed ensemble** of file-type specialists with a general fallback. "
        "For each file we detect the format (ELF, PE, PDF, JavaScript, …), pick the strongest "
        "route the calibrated policy allows for that format, and combine the chosen route's score "
        "with the general model's via the OR rule (a file is flagged iff any allowed route "
        "exceeds its calibrated threshold). The deployed router is what runs in production; the "
        "individual classifiers are ingredients.",
        "",
        "## Per-filetype performance (routed ensemble)",
        "",
        f"Calibrated against {_int(config.get('rows'))} dev-partition rows "
        f"({_int(config.get('malware'))} malware, {_int(config.get('benign'))} benign); "
        f"per-filetype numbers below are evaluated on **{n_eval} test-partition rows** "
        f"(SHA256-deterministic 12.5% locked holdout — never seen during training or calibration). "
        "EMBER columns reference Joyce et al., *KDD'25 — A Benchmark Dataset for Holistic Evaluation of Malware Classifiers*, Table 5.",
        "",
        *_ensemble_table(metrics, HEADLINE_FILETYPES),
        "",
        f"_Evaluation scope: {eval_note}. Numbers are raw discrimination metrics (continuous-domain ranking) — directly comparable to EMBER 2024's published AUC/PR. The deployed thresholded operating points (L=0..9 FP/M targets) are an orthogonal concern surfaced on the per-route cards._",
        "",
        "## What's in this bundle",
        "",
        f"- {_route_summary(config)} routes; runtime names are `az`, `az/<filegroup>`, `az/<filetype>`.",
        "- One cleave report per file, vectorized by the feature spec shipped with the selected route.",
        "- Per-route LightGBM specialists; the general model is also LightGBM trained on the full mixed corpus.",
        "",
        "## Where to look next",
        "",
        "- **[ENSEMBLE_MODEL.md](ENSEMBLE_MODEL.md)** — how the router decides, three-way (general/specialist/ensemble) per-filetype comparison, and operational FP/M policy levels.",
        "- **[GENERALIST_MODEL.md](GENERALIST_MODEL.md)** — the single-model fallback, per-filetype performance, EMBER-comparable.",
        "- **`filetypes/<name>/README.md`** — each specialist: its own training profile, single-model benchmark, and how the router uses it.",
        "",
        "## Reproducibility",
        "",
        f"- Calibration snapshot: `{config.get('calibration_snapshot_id')}`",
        f"- Score table: `{_short_hash(config.get('score_table_hash'))}`",
        f"- Model set: `{_short_hash(config.get('model_set_hash'))}`",
        "",
        "## Limits",
        "",
        "- Metrics are on the labeled corpus's dev (calibration) and test (locked headline) partitions. Deployment-time distribution shift can change real-world results.",
        "- Some narrow filetypes (powershell, ruby, jar, macho) have small benign sample sizes — the *raw* discrimination metric is reliable, but the per-FP-target threshold calibration on the per-route cards is noisier than wider-corpus routes (pe, elf, javascript). Treat the L0..L9 numbers there as guidance, not as confidence intervals.",
        "- Strict-FP/M operating points (L0–L3) are precision-floored by the dev/test partition sizes (~286k rows each, ~150k benign): a single FP moves the FP/M estimate by ~6. Reported numbers at those levels carry wider implicit CIs than the figure suggests.",
        "- The split is content-deduplicated by `canonical_sha256` (archives and their inner files always co-locate) but not family- or campaign-aware. Same actor / same packer can produce different content hashes that land on opposite sides of the split. Family-aware splitting is on the methodological roadmap; until then, generalization to truly unseen campaigns may be over-stated.",
        "",
        "## Dataset credits",
        "",
        "Training samples were sourced from the following malware corpora. This project wouldn't have gone anywhere without their service and support:",
        "",
        "- [MalwareBazaar](https://bazaar.abuse.ch/)",
        "- [VirusShare](https://virusshare.com/)",
        "- [Backstabber's Knife Collection](https://dasfreak.github.io/Backstabbers-Knife-Collection/)",
        "- [DataDog malicious-software-packages-dataset](https://github.com/DataDog/malicious-software-packages-dataset)",
        "- [VX Underground](https://vx-underground.org/)",
        "- [PyPI MalRegistry](https://github.com/lxyeternal/pypi_malregistry)",
        "- [Linux Malware Samples](https://github.com/MalwareSamples/Linux-Malware-Samples)",
        "- [Tim (Wadhwa-)Brown's Linux Malware Repo](https://github.com/timb-machine/linux-malware)",
        "- [Javascript Malware Collection](https://github.com/HynekPetrak/javascript-malware-collection)",
        "- [ObjectiveSee macOS Malware Collection](https://github.com/objective-see/Malware)",
        "- [Practical Security Analytics LLC PE Malware ML Dataset](https://practicalsecurityanalytics.com/pe-malware-machine-learning-dataset/)",
        "- [Ultimate RAT Collection](https://github.com/Cryakl/Ultimate-RAT-Collection)",
    ]
    _write(root / "README.md", "\n".join(lines))


def _write_ensemble_card(root: Path) -> None:
    """ENSEMBLE_MODEL.md — the routing-detail card.  Aimed at a reader trying
    to understand *what* the ensemble does (routing rules) and *whether* the
    routing helps (general vs specialist vs ensemble three-way)."""
    metrics = _load_per_filetype_metrics(root)
    n_eval = metrics.get("n_rows_evaluated", 0)
    lines = [
        "# Azoth — Routed Ensemble",
        "",
        "## How routing works",
        "",
        "Each file is processed in three steps:",
        "",
        "1. **Format detection.** The cleave report identifies the file's format (e.g. `elf`, `pe`, `javascript`).",
        "2. **Route selection.** `route_policies.json` defines, per format and per FP/M operating level, which routes are allowed (e.g. `[general, filegroups/native, filetypes/elf]`) and at what calibrated thresholds.",
        "3. **Decision.** Each allowed route scores the file with its own model + feature spec. The file is flagged at the chosen severity level iff any allowed route's score exceeds its threshold (the OR rule).",
        "",
        "Routing policies fall into a small set of patterns the calibrator picks per route per level:",
        "",
        "- `specialist_primary_with_escape`: file's own specialist is primary; general can still escalate if it scores high enough at its own threshold.",
        "- `or_general_primary`: general is primary; specialist may escalate.",
        "- `general_only` / `specialist_only` / `group_only`: that single route decides; others are ignored at this level.",
        "- `no_policy`: no route configuration meets the FP/M target at this level — the route effectively doesn't fire at this severity.",
        "",
        "## How the ensemble combiner works",
        "",
        "Per-file, the ensemble combines the available route scores via one of two strategies, picked per filetype to maximize ROC AUC on the test bucket:",
        "",
        "- **`specialist_priority`** (default): for each row, use the most specific route's *raw* score — specialist if available, else filegroup, else general. By construction this equals the specialist on filetype-X rows, so `ensemble ≥ specialist` always holds.",
        "- **`calibrated_max`**: per-route isotonic calibration via 5-fold CV, then `max` of the calibrated probabilities across allowed routes. Wins when the specialist alone is weak and the cross-model signal genuinely adds discrimination — typically on filetypes with thin specialist training data (e.g. `pdf`, `docx`, `xml`).",
        "",
        "The naive `max(raw_general, raw_filegroup, raw_specialist)` we used in earlier drafts is *not* used as the headline number — raw scores live on different scales, so it can rank worse than the specialist alone. It's recorded in `per_filetype_metrics.json` as `ensemble_strategies.naive_max` for diagnostic comparison only.",
        "",
        "## General vs specialist vs ensemble",
        "",
        f"Three views of each filetype, evaluated on **{n_eval} test-partition rows** "
        "(SHA256-deterministic 12.5% locked holdout — never seen during training or "
        "calibration). 'Ensemble' uses the per-filetype winning strategy from above; "
        "'Routing policy' is the deployed thresholded decision at the default "
        "operating level (a separate concern from the raw AUC of the combiner).",
        "",
        *_three_way_table(metrics, HEADLINE_FILETYPES),
        "",
        "Reading the table: ensemble ≥ specialist holds for every filetype by design. When `strategy = specialist_priority`, the ensemble's column matches the specialist's. When `strategy = calibrated_max`, the routing-free combiner beats the specialist alone — those filetypes benefit most from cross-model signal.",
        "",
        "## Operational FP/M dialing (deployment knob)",
        "",
        "Independently of the AUC/PR metrics above, the bundle is calibrated at ten thresholded operating points (L0…L9) per severity. Each level corresponds to a per-million false-positive budget; the calibrator picks the per-route thresholds that maximize true positives subject to that global budget.",
        "",
        "**This is a deployment dial, not a model-quality result.** When a route shows `no_policy` at a given level, it means no threshold for that route fits inside the global FP budget at that level — which is a function of corpus size, route benign-tail shape, and the FP target, not the model's discrimination ability. Dialing the operating level up admits more routes; dialing down enforces a stricter FP target. Per-route operating tables live in each `filetypes/<name>/README.md`.",
        "",
        _global_policy_table(root),
        "",
        "Default deploy: L3 for hostile, L5 for suspicious. The headline AUC/PR/F1 figures elsewhere in this bundle are about the model's ranking ability — they don't change with the operating level.",
    ]
    _write(root / "ENSEMBLE_MODEL.md", "\n".join(lines))


def _write_generalist_card(root: Path) -> None:
    """GENERALIST_MODEL.md — single-model card for the general classifier.
    Reference numbers; the deployed product is the ensemble (see ENSEMBLE_MODEL.md)."""
    metrics = _load_per_filetype_metrics(root)
    train_config = _general_train_config(root)
    evaluation = _general_evaluation(root)
    eval_metrics = evaluation.get("metrics") or {}
    feature_spec_path = root / "general" / "feature_spec.json"
    n_features = _feature_count(feature_spec_path, evaluation.get("n_features"))
    lines = [
        "# Azoth — Generalist Model",
        "",
        "Single LightGBM classifier trained on the full mixed corpus across all supported filetypes. "
        "Equivalent to EMBER 2024's \"All files\" classifier in spirit (Table 5, top section).",
        "",
        "**This model alone is not the deployed product.** It is one of the routes the routed ensemble can choose — see [ENSEMBLE_MODEL.md](ENSEMBLE_MODEL.md). Numbers below are reported for transparency and direct EMBER-comparison.",
        "",
        "## Per-filetype performance (general model only)",
        "",
        "Test-partition only (SHA256-deterministic 12.5% locked holdout, never trained on or calibrated against). EMBER columns reference Joyce et al., *KDD'25*, Table 5 'All files → X' rows.",
        "",
        *_generalist_table(metrics, HEADLINE_FILETYPES),
        "",
        "## Training",
        "",
        f"- Algorithm: {_model_algo(train_config)}",
        f"- Feature spec: `general/feature_spec.json` ({_int(n_features)} features)",
        "- Trained on the full mixed corpus across all supported filetypes "
        "(75% train / 12.5% dev / 12.5% test, SHA256-deterministic split). "
        "Calibrators and L0..L9 thresholds are fit on dev; the metrics in this "
        "card are reported on the locked test partition (never seen during "
        "training or calibration).",
        "",
        "## Hard-pool reference (training-time evaluation)",
        "",
        f"- Accuracy: {_pct(eval_metrics.get('accuracy'))}",
        f"- F1: {_num(eval_metrics.get('f1'), 4)}",
        f"- ROC AUC: {_num(eval_metrics.get('roc_auc'), 4)}",
        f"- Average Precision: {_num(eval_metrics.get('avg_precision'), 4)}",
        f"- Brier: {_num(eval_metrics.get('brier'), 4)}",
        "",
        "These are the numbers reported during training on the hard-pool holdout (a curated subset). The per-filetype table above is the better reference for production expectations.",
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
