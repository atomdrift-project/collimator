"""Tests for scripts/azoth_train_best.py best-run picker + env builder.

The picker is the bridge that lets `make train-best` etc. pull the latest
autocollie discovery for a route into a regular `make experiment` invocation.
Test the selection rule, the env mapping, and the caller-override precedence.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

_SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "azoth_train_best.py"
_spec = importlib.util.spec_from_file_location("azoth_train_best", _SCRIPT)
assert _spec is not None and _spec.loader is not None
_mod = importlib.util.module_from_spec(_spec)
sys.modules["azoth_train_best"] = _mod
_spec.loader.exec_module(_mod)


def _write_run(runs_dir: Path, key: str, route: str, *, f1: float,
               save_all: bool = False, timestamp: str = "2026-01-01",
               train_config: dict | None = None,
               feature_env: dict | None = None,
               experiment_spec: dict | None = None,
               idea: str = "test") -> Path:
    runs_dir.mkdir(parents=True, exist_ok=True)
    payload = {
        "experiment_key": key,
        "route": route,
        "idea": idea,
        "timestamp": timestamp,
        "save_all_seeds": save_all,
        "sampled_test_metrics": {"f1": f1},
        "train_config": train_config or {},
        "feature_env": feature_env or {},
        "experiment_spec": experiment_spec or {},
    }
    p = runs_dir / f"{key}.json"
    p.write_text(json.dumps(payload))
    return p


def test_select_best_picks_highest_f1(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    _write_run(runs, "low", "general", f1=0.95)
    _write_run(runs, "high", "general", f1=0.99)
    best = _mod._select_best_run(runs, "general")  # type: ignore[attr-defined]
    assert best is not None
    assert best["experiment_key"] == "high"


def test_select_best_filters_by_route(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    _write_run(runs, "ggood", "general", f1=0.99)
    _write_run(runs, "bbest", "filetypes/perl", f1=1.0)  # higher F1 but wrong route
    best = _mod._select_best_run(runs, "general")  # type: ignore[attr-defined]
    assert best is not None
    assert best["experiment_key"] == "ggood"


def test_select_best_prefers_save_all_seeds_on_tie(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    _write_run(runs, "single", "general", f1=0.99, save_all=False, timestamp="2026-02-01")
    _write_run(runs, "averaged", "general", f1=0.99, save_all=True, timestamp="2026-01-01")
    best = _mod._select_best_run(runs, "general")  # type: ignore[attr-defined]
    assert best is not None
    assert best["experiment_key"] == "averaged"


def test_select_best_prefers_newer_timestamp_on_full_tie(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    _write_run(runs, "older", "general", f1=0.99, save_all=True, timestamp="2026-01-01")
    _write_run(runs, "newer", "general", f1=0.99, save_all=True, timestamp="2026-03-01")
    best = _mod._select_best_run(runs, "general")  # type: ignore[attr-defined]
    assert best is not None
    assert best["experiment_key"] == "newer"


def test_select_best_returns_none_when_no_matches(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    _write_run(runs, "x", "filetypes/perl", f1=1.0)
    best = _mod._select_best_run(runs, "general")  # type: ignore[attr-defined]
    assert best is None


def test_select_best_skips_feature_spec_sidecars(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    _write_run(runs, "real", "general", f1=0.99)
    # A feature spec sidecar that happens to have a "route" field shouldn't be considered.
    sidecar = runs / "real_feature_spec.json"
    sidecar.write_text(json.dumps({"route": "general", "sampled_test_metrics": {"f1": 1.0}}))
    best = _mod._select_best_run(runs, "general")  # type: ignore[attr-defined]
    assert best is not None
    assert best["experiment_key"] == "real"


def test_select_best_tolerates_corrupt_json(tmp_path: Path) -> None:
    runs = tmp_path / "runs"
    _write_run(runs, "good", "general", f1=0.99)
    (runs / "broken.json").write_text("{not json")
    best = _mod._select_best_run(runs, "general")  # type: ignore[attr-defined]
    assert best is not None
    assert best["experiment_key"] == "good"


def test_resolve_env_maps_train_config_to_exp_vars() -> None:
    run = {
        "train_config": {
            "n_estimators": 400,
            "max_depth": 12,
            "learning_rate": 0.05,
            "extra_trees": True,
            "scale_pos_weight_mult": 1.5,
            "monotone_constraints": {"x": 1},  # not in mapping — must be skipped
        },
        "feature_env": {"COLLIMATOR_FORMAT_HINTS": "1", "COLLIMATOR_FOO": "bar"},
        "experiment_spec": {"train_samples": 600000, "seed_search_k": 3},
        "filters": {"min_malware_training_score": 5},
        "seed": 42,
    }
    env = _mod._resolve_env(run, {})  # type: ignore[attr-defined]
    assert env["EXP_ESTIMATORS"] == "400"
    assert env["EXP_MAX_DEPTH"] == "12"
    assert env["EXP_LEARNING_RATE"] == "0.05"
    assert env["EXP_EXTRA_TREES"] == "1"
    assert env["EXP_SCALE_POS_WEIGHT_MULT"] == "1.5"
    assert env["EXP_TRAIN_SAMPLES"] == "600000"
    assert env["EXP_SEED_SEARCH_K"] == "3"
    assert env["EXP_MIN_MALWARE_SCORE"] == "5"
    assert env["SEED"] == "42"
    assert env["COLLIMATOR_FORMAT_HINTS"] == "1"
    assert env["COLLIMATOR_FOO"] == "bar"
    # Unmapped knobs don't leak in.
    assert "monotone_constraints" not in env


def test_resolve_env_caller_extras_override_run() -> None:
    run = {
        "train_config": {"n_estimators": 400},
        "feature_env": {"COLLIMATOR_FORMAT_HINTS": "0"},
    }
    extra = {"EXP_ESTIMATORS": "100", "COLLIMATOR_FORMAT_HINTS": "1", "DB": "x://y"}
    env = _mod._resolve_env(run, extra)  # type: ignore[attr-defined]
    assert env["EXP_ESTIMATORS"] == "100"  # caller wins
    assert env["COLLIMATOR_FORMAT_HINTS"] == "1"  # caller wins
    assert env["DB"] == "x://y"  # passes through


def test_resolve_env_skips_none_values() -> None:
    run = {
        "train_config": {"n_estimators": 400, "threshold_fpr_target": None},
    }
    env = _mod._resolve_env(run, {})  # type: ignore[attr-defined]
    assert env["EXP_ESTIMATORS"] == "400"
    assert "EXP_THRESHOLD_FPR_TARGET" not in env


def test_format_env_value_handles_bool_and_float() -> None:
    assert _mod._format_env_value(True) == "1"  # type: ignore[attr-defined]
    assert _mod._format_env_value(False) == "0"  # type: ignore[attr-defined]
    assert _mod._format_env_value(0.05) == "0.05"  # type: ignore[attr-defined]
    assert _mod._format_env_value(400) == "400"  # type: ignore[attr-defined]
    assert _mod._format_env_value("auto") == "auto"  # type: ignore[attr-defined]
