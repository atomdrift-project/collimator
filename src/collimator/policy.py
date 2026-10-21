"""Frozen deployment decisions and disjoint selection/reporting populations."""

from __future__ import annotations

import numpy as np
from scipy.special import expit

from . import data


def partition_table(table, partition: str) -> dict:
    """Subset a score table without changing route order or row alignment."""
    if "sha_bucket" not in table:
        raise ValueError("score table lacks canonical partitions; regenerate scores")
    buckets = np.asarray(table["sha_bucket"])
    if partition == "dev":
        mask = (buckets >= data.TEST_BUCKET_MAX) & (buckets < data.DEV_BUCKET_MAX)
    elif partition == "test":
        mask = buckets < data.TEST_BUCKET_MAX
    else:
        raise ValueError("selection must use dev; reporting must use test")
    return {
        key: (np.asarray(table[key])[:, mask] if key == "scores" else
              np.asarray(table[key])[mask] if key in {
                  "row_ids", "labels", "file_types", "file_groups", "sha_bucket",
              } else table[key])
        for key in table
    }


def margin(scores: dict[str, np.ndarray], decision: dict, size: int) -> np.ndarray:
    """Signed distance from a frozen policy's decision, matching scan's f32 compare."""
    result = np.full(size, -np.inf, dtype=np.float32)
    blend = decision.get("blend")
    if blend:
        routes, weights = blend["routes"], blend["weights"]
        if not routes or len(routes) != len(weights):
            raise ValueError("invalid blend routes/weights")
        valid = np.ones(size, dtype=bool)
        z = np.full(size, float(np.float32(blend["intercept"])), dtype=np.float64)
        for route, weight in zip(routes, weights, strict=True):
            if route not in scores:
                return result
            p = np.asarray(scores[route], dtype=np.float64)
            valid &= np.isfinite(p)
            p = np.clip(p, 1e-6, 1 - 1e-6)
            z += float(np.float32(weight)) * np.log(p / (1 - p))
        result[valid] = expit(z[valid]).astype(np.float32) - np.float32(blend["threshold"])
        return result
    for route, threshold in (decision.get("thresholds") or {}).items():
        if route not in scores or threshold is None or not 0 <= np.float32(threshold) <= 1:
            continue
        p = np.asarray(scores[route], dtype=np.float32)
        np.maximum(result, np.where(np.isfinite(p), p - np.float32(threshold), -np.inf), out=result)
    return result


def swept_margin(scores: dict[str, np.ndarray], levels: list[dict], level: int,
                 size: int, *, severity: str = "hostile") -> np.ndarray:
    """Scan flags a file if any policy at or below the requested level fires."""
    result = np.full(size, -np.inf, dtype=np.float32)
    for item in levels:
        if int(item["level"]) <= level:
            entry = item.get(severity) or {}
            decision = entry.get("best", entry) or {}
            np.maximum(result, margin(scores, decision, size), out=result)
    return result


def routed_margin(scores: dict[str, np.ndarray], config: dict, policies: dict,
                  filetype: str, level: int, size: int, *, severity: str = "hostile") -> np.ndarray:
    """Apply the filetype grid, or scan's general-threshold fallback."""
    levels = routing_levels(scores, config, policies, filetype, severity=severity)
    return swept_margin(scores, levels, level, size, severity=severity)


def routing_levels(scores: dict, config: dict, policies: dict, filetype: str,
                   *, severity: str = "hostile") -> list[dict]:
    route = policies.get("routes", {}).get(f"filetypes/{filetype}", {})
    levels = route.get("levels", [])
    for item in levels:
        best = item.get(severity, {}).get("best") or {}
        if best.get("blend") or any(
                value is not None and 0 <= np.float32(value) <= 1
                for value in (best.get("thresholds") or {}).values()):
            return levels
    # scan omits grids with no usable policy and uses its general fallback.
    fallback = []
    for item in config["levels"]:
        threshold = item.get(severity, {}).get("thresholds", {}).get("general", 1.0)
        fallback.append({"level": item["level"], severity: {
            "thresholds": {name: threshold for name in scores},
        }})
    return fallback


def first_firing_level(scores: dict, levels: list[dict], size: int, level: int,
                       *, severity: str = "hostile") -> tuple[np.ndarray, np.ndarray]:
    """Evaluate each saved policy once, retaining O(rows) state."""
    first = np.full(size, np.iinfo(np.int64).max, dtype=np.int64)
    rank = np.full(size, -np.inf, dtype=np.float32)
    for item in sorted(levels, key=lambda x: int(x["level"])):
        current = int(item["level"])
        entry = item.get(severity) or {}
        distance = margin(scores, entry.get("best", entry) or {}, size)
        first[(distance >= 0) & (first > current)] = current
        if current <= level:
            np.maximum(rank, distance, out=rank)
    return first, rank


def fixed_metrics(labels: np.ndarray, ranking: np.ndarray,
                  first: np.ndarray, grid: list[int], level: int, *, with_ci: bool = True,
                  probabilities: bool = False) -> dict:
    """Ranking diagnostics plus observed decisions; never fit on report labels."""
    from scipy.stats import beta
    from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score

    positive = labels == 1
    n_pos, n_neg = int(positive.sum()), int((~positive).sum())
    rank = np.nan_to_num(ranking, nan=-1e30, neginf=-1e30, posinf=1e30)
    out = {"n_evaluated": len(labels),
           "roc_auc": float(roc_auc_score(labels, rank)) if n_pos and n_neg else None,
           "pr_auc": float(average_precision_score(labels, rank)) if n_pos else None,
           "brier": float(brier_score_loss(labels, rank)) if probabilities and len(labels) else None}
    for current in grid:
        hit = first <= current
        tp, fp = int((hit & positive).sum()), int((hit & ~positive).sum())
        field = f"recall_at_{current}_per_100M"
        out[field] = tp / n_pos if n_pos else None
        out[f"fp_at_{current}_per_100M"] = fp / n_neg * 1e8 if n_neg else None
        if with_ci and n_pos:
            out[field + "_ci_low"] = float(beta.ppf(.025, tp, n_pos - tp + 1)) if tp else 0.
            out[field + "_ci_high"] = float(beta.ppf(.975, tp + 1, n_pos - tp)) if tp < n_pos else 1.
        if current == level:
            out.update(tp=tp, fp=fp, tn=n_neg - fp, fn=n_pos - tp,
                       f1=2 * tp / (n_pos + tp + fp) if n_pos + tp + fp else 0.,
                       recall=out[field], fp_per_100M=out[f"fp_at_{current}_per_100M"])
    return out


def report(table, config: dict, policies: dict, *, level: int, severity: str = "hostile",
           with_ci: bool = True) -> dict:
    """Report locked-test performance of saved production decisions."""
    table = partition_table(table, "test")
    labels, filetypes = table["labels"], table["file_types"]
    scores = dict(zip(map(str, table["route_names"]), table["scores"], strict=True))
    grid = sorted({level} | {int(item["level"]) for item in config["levels"]})
    # Retain only the two ensemble arrays needed for reporting: margin at the
    # requested operating point and first firing level. Avoid rows × levels RAM.
    first = np.full(len(labels), np.iinfo(np.int64).max, dtype=np.int64)
    rank = np.full(len(labels), -np.inf, dtype=np.float32)
    allowed_routes = {}
    for ft in np.unique(filetypes):
        mask = filetypes == ft
        subset = {name: values[mask] for name, values in scores.items()}
        levels = routing_levels(subset, config, policies, str(ft), severity=severity)
        members = set()
        for item in levels:
            if int(item["level"]) > level:
                continue
            entry = item.get(severity) or {}
            chosen = entry.get("best", entry) or {}
            members.update((chosen.get("thresholds") or {}).keys())
            members.update((chosen.get("blend") or {}).get("routes", []))
        allowed_routes[str(ft)] = sorted(
            name for name in members if name in subset and np.isfinite(subset[name]).any())
        first[mask], rank[mask] = first_firing_level(
            subset, levels, int(mask.sum()), level, severity=severity)

    def entry(mask, specialist=None):
        y = labels[mask]
        result = {"n_files": len(y), "n_malware": int((y == 1).sum()), "n_benign": int((y == 0).sum()),
                  "ensemble_strategy": "deployed_policy",
                  "ensemble": fixed_metrics(y, rank[mask], first[mask], grid, level, with_ci=with_ci)}
        for key, route in (("general", "general"), ("specialist", specialist)):
            if route not in scores:
                continue
            valid = mask & np.isfinite(scores[route])
            p = scores[route][valid]
            alone = {route: p}
            fired, _ = first_firing_level(alone, config["levels"], len(p), level, severity=severity)
            result[key] = fixed_metrics(labels[valid], p, fired, grid, level, with_ci=with_ci, probabilities=True)
        return result

    return {
        "schema": "azoth.per_filetype_metrics.v3",
        "calibration_snapshot_id": config.get("calibration_snapshot_id"),
        "operating_level": level, "severity": severity, "evaluated_on": "test_bucket_only",
        "calibration_fit_partition": config.get("fit_partition"),
        "decision_rule": "saved_policy_sweep", "ranking_score": "signed_policy_margin",
        "n_rows_evaluated": len(labels), "with_ci": with_ci, "stacked_diagnostics": False,
        "filetypes": {str(ft): dict(entry(filetypes == ft, f"filetypes/{ft}"),
                                   ensemble_allowed_routes=allowed_routes[str(ft)])
                      for ft in np.unique(filetypes)},
        "filegroups": {str(fg): entry(table["file_groups"] == fg, f"filegroups/{fg}")
                       for fg in np.unique(table["file_groups"]) if fg},
        "all_files": entry(np.ones(len(labels), dtype=bool)),
    }
