#!/usr/bin/env python3
"""Write concise README files for an Azoth model bundle."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from typing import Any


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
    path = root / "global_policy_metrics.json"
    if not path.exists():
        return ""
    with open(path) as f:
        data = json.load(f)
    lines = [
        "| L | H recall | H FP/1M | S recall | S FP/1M |",
        "| ---: | ---: | ---: | ---: | ---: |",
    ]
    for level_no in (0, 5, 9):
        level = next(item for item in data["levels"] if int(item["level"]) == level_no)
        h = level["hostile"]
        s = level["suspicious"]
        lines.append(
            "| "
            f"{level_no} | {_pct(h.get('recall'))} | {_num(h.get('fp_per_million'), 2)} | "
            f"{_pct(s.get('recall'))} | {_num(s.get('fp_per_million'), 2)} |"
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
    return _lightgbm_model_config(root / "general" / "model.txt")


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
    with open(path / "benchmark.json") as f:
        data = json.load(f)
    metrics = data.get("metrics") or {}
    name = data["name"]
    kind = data["kind"]
    file_types = ", ".join(f"`{item}`" for item in data.get("file_types", []))
    warning = ""
    if metrics.get("roc_auc") is not None and float(metrics["roc_auc"]) <= 0.501:
        warning = (
            "\n- Note: benchmark AUC is degenerate on this split; keep the artifact "
            "for coverage, but rely on routed full-corpus calibration before using it."
        )
    lines = [
        f"# Azoth {kind.title()} `{name}`",
        "",
        f"Specialist model for {file_types}.",
        "",
        f"- Inputs: shared general `feature_spec.json` ({data.get('n_features')} features); policy `{data.get('feature_spec_policy')}`.",
        "- Feature families:",
        _feature_summary(),
        f"- Technique: {_model_algo(data.get('train_config'))}",
        f"- Training rows: {_int(data.get('train_rows'))} "
        f"({_int(data.get('train_malware'))} malware, {_int(data.get('train_benign'))} benign).",
        f"- Benchmark rows: {_int(data.get('benchmark_rows'))} "
        f"({_int(data.get('benchmark_malware'))} malware, "
        f"{_int(data.get('benchmark_benign'))} benign).",
        f"- Benchmark AUC/AP/F1: {_num(metrics.get('roc_auc'), 4)} / "
        f"{_num(metrics.get('avg_precision'), 4)} / {_num(metrics.get('max_f1'), 4)}.",
        warning,
        "",
        _level_table(data["levels"]),
    ]
    route_prefix = "filegroups" if kind == "filegroup" else "filetypes"
    policy_lines = _policy_levels(root, f"{route_prefix}/{name}")
    if policy_lines:
        lines.extend(["", "## Routed Policy", "", *policy_lines])
    _write(path / "README.md", "\n".join(line for line in lines if line != ""))


def _write_bundle(root: Path) -> None:
    with open(root / "config.json") as f:
        config = json.load(f)
    general_config = _general_train_config(root)
    lines = [
        "# Azoth Bundle",
        "",
        "Routed ensemble of the general model plus eligible filegroup and filetype specialists.",
        "",
        "- Inputs: one cleave report vectorized with the shared general feature spec.",
        "- Feature families:",
        _feature_summary(),
        f"- Base technique: {_model_algo(general_config)}",
        "- Decision rule: route-level OR ensemble calibrated against the full score-cache corpus.",
        "- Runtime route: score `az`, plus `az/<filegroup>` and `az/<filetype>` when calibrated.",
        "- At level L, a file is flagged when any routed score crosses its stored threshold.",
        "- Threshold search maximizes `TP(union)` subject to `FP(union) <= floor(benign * target_L / 1e6)`.",
        "- A specialist is kept only when it adds marginal true positives without breaking that union FP cap.",
        f"- Calibration snapshot: `{config.get('calibration_snapshot_id')}`.",
        f"- Calibration rows: {_int(config.get('rows'))} "
        f"({_int(config.get('malware'))} malware, {_int(config.get('benign'))} benign).",
        f"- Models: {len(config.get('models', []))} routes.",
        "",
        "## Effective Global Policy",
        "",
        _global_policy_table(root),
        "",
        _level_table(config["levels"]),
    ]
    _write(root / "MODEL.md", "\n".join(lines))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--azoth-root", type=Path, default=Path("out/models/azoth"))
    args = parser.parse_args()
    root = args.azoth_root
    _write_bundle(root)
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
