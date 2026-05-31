#!/usr/bin/env python3
"""Train tail-contrast candidates for every eligible Azoth filetype."""

from __future__ import annotations

import argparse
import json
import logging
import math
import shutil
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

from collimator import bundle, data, features, thresholds

sys.path.insert(0, str(Path(__file__).resolve().parent))
from azoth_specialist_suite import _eligible_filetypes, _fetch_rows, _ids_labels  # noqa: E402
from elf_ensemble_experiments import (  # noqa: E402
    _acquittal_levels,
    _best_l5_l9,
    _elf_local_l5_l9,
    _elf_local_levels,
    _general_baseline,
    _matrix,
    _or_levels,
    _replacement_levels,
    _save_model,
    _score_estimator,
    _train_lgbm_classifier,
)

LOG = logging.getLogger("azoth_tail_contrast_sweep")


def _json_clean(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): _json_clean(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_json_clean(v) for v in value]
    if isinstance(value, float) and math.isnan(value):
        return None
    if isinstance(value, np.floating):
        f = float(value)
        return None if math.isnan(f) else f
    if isinstance(value, np.integer):
        return int(value)
    return value


def _pct(value: float | None) -> str:
    if value is None or math.isnan(float(value)):
        return "-"
    return f"{100.0 * float(value):.2f}%"


def _l5_hostile(summary: dict[str, Any], rule: str) -> dict[str, Any]:
    return summary[rule]["l5_hostile"]


def _best_rule(summary: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    candidates = [(rule, _l5_hostile(summary, rule)) for rule in ("or", "replacement", "acquittal")]
    return max(candidates, key=lambda item: (float(item[1]["recall"]), -int(item[1]["fp"])))


def _best_local_policy(local_level: dict[str, Any]) -> tuple[str, dict[str, Any]]:
    candidates = list(local_level.items())
    return max(candidates, key=lambda item: (float(item[1]["recall"]), -int(item[1]["fp"])))


def _write_markdown(path: Path, payload: dict[str, Any]) -> None:
    rows = sorted(
        payload["results"],
        key=lambda item: (
            float(item.get("best_l5_hostile", {}).get("recall") or -1.0),
            int(item.get("calibration_rows") or 0),
        ),
        reverse=True,
    )
    lines = [
        "# Azoth Tail-Contrast Sweep",
        "",
        f"- Timestamp: `{payload['timestamp']}`",
        f"- Score snapshot: `{payload['score_snapshot_id']}`",
        f"- Eligible filetypes: {payload['eligible_filetypes']}",
        f"- Completed: {sum(1 for r in payload['results'] if not r.get('error'))}",
        "",
        "| Filetype | Train bad/good | Cal bad/good | Best rule | L5 hostile recall @ FP | Local best | Local F1 | Local accuracy |",
        "|---|---:|---:|---|---:|---:|---:|---:|",
    ]
    for item in rows:
        if item.get("error"):
            lines.append(f"| `{item['filetype']}` | - | - | error | - | - | - | - |")
            continue
        best = item["best_l5_hostile"]
        local_policy = item["local_l5_hostile_policy"]
        local = item["local_l5_hostile_best"]
        lines.append(
            "| "
            f"`{item['filetype']}` | "
            f"{item['train_malware']}/{item['train_benign']} | "
            f"{item['calibration_malware']}/{item['calibration_benign']} | "
            f"{item['best_rule']} | "
            f"{_pct(best.get('recall'))} @ {best.get('fp')} | "
            f"{local_policy} {_pct(local.get('recall'))} @ {local.get('fp')} | "
            f"{_pct(local.get('f1'))} | "
            f"{_pct(local.get('accuracy'))} |",
        )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n")


def _load_existing(output: Path) -> dict[str, Any] | None:
    if not output.exists():
        return None
    with open(output) as f:
        return json.load(f)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--general-scores", type=Path, default=Path("out/models/azoth/general/threshold_scores.npz"))
    parser.add_argument("--general-spec", type=Path, default=Path("out/models/azoth/general/feature_spec.json"))
    parser.add_argument("--output-root", type=Path, default=Path("out/models/azoth-tail-filetypes"))
    parser.add_argument("--output", type=Path, default=Path("out/models/azoth-tail-filetypes/results.json"))
    parser.add_argument("--markdown", type=Path, default=Path("experiments/AZOTH-TAIL-CONTRAST.md"))
    parser.add_argument("--min-bad", type=int, default=50)
    parser.add_argument("--min-good", type=int, default=50)
    parser.add_argument("--only", action="append", default=[])
    parser.add_argument("--limit", type=int, default=0)
    parser.add_argument("--skip-existing", action="store_true")
    parser.add_argument("--workers", type=int, default=0)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--log-level", default="INFO")
    args = parser.parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper()),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    general_spec = features.FeatureSpec.load(args.general_spec)
    cache = np.load(args.general_scores)
    row_ids = cache["row_ids"].astype(np.int64)
    labels = cache["labels"].astype(np.int8)
    general_probs = cache["probs"].astype(np.float32)
    max_id = int(cache["corpus_requested_max_id"]) or int(cache["corpus_max_row_id"])
    row_index = {int(row_id): idx for idx, row_id in enumerate(row_ids)}
    baseline_levels = _general_baseline(labels, general_probs)
    general_l500 = next(item for item in baseline_levels if item["level"] == 500)["hostile"]
    l500_threshold = float(general_l500["thresholds"]["general"])

    targets = _eligible_filetypes(
        args.db,
        max_id=max_id,
        min_score=None,
        min_bad=args.min_bad,
        min_good=args.min_good,
    )
    if args.only:
        wanted = set(args.only)
        targets = [target for target in targets if target["name"] in wanted]
    if args.limit:
        targets = targets[: args.limit]
    LOG.info("eligible filetypes: %d", len(targets))

    existing = _load_existing(args.output)
    existing_results = {
        str(item["filetype"]): item
        for item in (existing or {}).get("results", [])
        if not item.get("error")
    }
    results: list[dict[str, Any]] = []

    for pos, target in enumerate(targets, start=1):
        filetype = str(target["name"])
        output_dir = args.output_root / "filetypes" / filetype
        LOG.info("[%d/%d] %s: starting tail_contrast", pos, len(targets), filetype)
        if args.skip_existing and bundle.has_model(output_dir) and filetype in existing_results:
            LOG.info("%s: using existing result", filetype)
            results.append(existing_results[filetype])
            continue
        try:
            rows_all = _fetch_rows(args.db, file_types=(filetype,), max_id=max_id, min_score=None)
            train_rows = _ids_labels(rows_all, test=False)
            route_rows = [
                (row_id, label)
                for row_id, label, _is_test, _ft in rows_all
                if row_id in row_index
            ]
            if not route_rows:
                raise RuntimeError("no calibration rows in general score cache")
            train_malware = sum(label == 1 for _row_id, label in train_rows)
            train_benign = sum(label == 0 for _row_id, label in train_rows)
            calibration_malware = sum(label == 1 for _row_id, label in route_rows)
            calibration_benign = sum(label == 0 for _row_id, label in route_rows)
            LOG.info(
                "%s: train=%d (%d bad/%d good), calibration=%d (%d bad/%d good)",
                filetype,
                len(train_rows),
                train_malware,
                train_benign,
                len(route_rows),
                calibration_malware,
                calibration_benign,
            )
            x_train, y_train = _matrix(args.db, train_rows, general_spec, args.workers)
            route_indices = np.asarray([row_index[row_id] for row_id, _label in route_rows], dtype=np.int64)
            x_route, _y_route = _matrix(args.db, route_rows, general_spec, args.workers)
            train_global_indices = np.asarray(
                [row_index[row_id] for row_id, _label in train_rows if row_id in row_index],
                dtype=np.int64,
            )
            weights = np.ones(len(y_train), dtype=np.float32)
            if len(train_global_indices) == len(y_train):
                train_general_scores = general_probs[train_global_indices]
                hard_pos = (y_train == 1) & (train_general_scores < l500_threshold)
                if np.any(y_train == 0):
                    hard_neg_cut = np.quantile(train_general_scores[y_train == 0], 0.995)
                    hard_neg = (y_train == 0) & (train_general_scores >= hard_neg_cut)
                else:
                    hard_neg = np.zeros(len(y_train), dtype=bool)
                weights[hard_pos] = 8.0
                weights[hard_neg] = 12.0
            tail = _train_lgbm_classifier(x_train, y_train, sample_weight=weights, seed=args.seed)
            output_dir.mkdir(parents=True, exist_ok=True)
            _save_model(tail, output_dir)
            shutil.copy2(args.general_spec, output_dir / "feature_spec.json")
            tail_probs = _score_estimator(tail, x_route)
            rules = {
                "or": _or_levels(labels, general_probs, route_indices, tail_probs),
                "replacement": _replacement_levels(labels, general_probs, route_indices, tail_probs),
                "acquittal": _acquittal_levels(labels, general_probs, route_indices, tail_probs),
            }
            summary = {rule: _best_l5_l9(levels) for rule, levels in rules.items()}
            best_rule, best_l5 = _best_rule(summary)
            local = _elf_local_l5_l9(_elf_local_levels(labels, general_probs, route_indices, tail_probs))
            local_l5_policy, local_l5_best = _best_local_policy(local["l5_hostile"])
            local_l9_policy, local_l9_best = _best_local_policy(local["l9_hostile"])
            item = {
                "filetype": filetype,
                "output_dir": str(output_dir),
                "train_rows": len(train_rows),
                "train_malware": train_malware,
                "train_benign": train_benign,
                "calibration_rows": len(route_rows),
                "calibration_malware": calibration_malware,
                "calibration_benign": calibration_benign,
                "best_rule": best_rule,
                "best_l5_hostile": best_l5,
                "summary": summary,
                "local_l5_hostile": local["l5_hostile"],
                "local_l9_hostile": local["l9_hostile"],
                "local_l5_hostile_policy": local_l5_policy,
                "local_l5_hostile_best": local_l5_best,
                "local_l9_hostile_policy": local_l9_policy,
                "local_l9_hostile_best": local_l9_best,
            }
            results.append(item)
            LOG.info(
                "%s: best=%s L5 hostile %.2f%% @ %s FP",
                filetype,
                best_rule,
                100.0 * float(best_l5["recall"]),
                best_l5["fp"],
            )
        except Exception as exc:  # noqa: BLE001
            LOG.exception("%s: failed", filetype)
            results.append({"filetype": filetype, "error": str(exc)})
        payload = {
            "timestamp": datetime.now(UTC).isoformat(),
            "schema": "azoth.tail_contrast_sweep.v1",
            "db": str(args.db),
            "score_snapshot_id": max_id,
            "general_scores": str(args.general_scores),
            "general_spec": str(args.general_spec),
            "output_root": str(args.output_root),
            "min_bad": args.min_bad,
            "min_good": args.min_good,
            "eligible_filetypes": len(targets),
            "results": results,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w") as f:
            json.dump(_json_clean(payload), f, indent=2, allow_nan=False)
        _write_markdown(args.markdown, _json_clean(payload))

    print(f"wrote {args.output}")
    print(f"wrote {args.markdown}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
