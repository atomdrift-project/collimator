"""Drop weak / undeployable specialist routes from an azoth bundle.

Two failure modes used to abort the whole deploy:

  1. A specialist whose home-filetype PR-AUC does not beat the general
     route — i.e. a model too weak to justify its own route. These slipped
     through specialist *selection* (which gates only on row support,
     ``min_bad``/``min_good``) and were only ever caught — by accident —
     when their LightGBM->ONNX export tripped the float32 parity check.
  2. A specialist whose ONNX export legitimately fails parity (e.g. a
     float32 boundary leaf-flip on a near-threshold sample row).

In both cases the right answer is the same: the specialist carries no
defensible signal, so drop its route and let the filetype fall back to the
general (and filegroup) routes it already shares an ensemble with. A weak
model must never abort the pipeline.

Pruning rewrites the bundle so a dropped ``filetypes/<ft>`` route becomes
indistinguishable from a normally specialist-less filetype (e.g.
``filetypes/asar``: ``models: ["general"]``, members reference only the
fallback routes, ``dominated_by_specialist: false``). The filetype's own
routing *policy* is kept — only the specialist *member* is removed — so the
filetype is still scored, just by its fallback ensemble.

``general`` is never prunable: it is the fallback of last resort.
"""

from __future__ import annotations

import json
import logging
import shutil
from pathlib import Path
from typing import Any

LOG = logging.getLogger("route_prune")

PROTECTED_ROUTES = frozenset({"general"})


DEFAULT_PR_AUC_TOLERANCE = 0.005


def weak_filetype_specialists(
    per_filetype_metrics: dict[str, Any],
    *,
    tolerance: float = DEFAULT_PR_AUC_TOLERANCE,
) -> dict[str, dict[str, float]]:
    """Return ``{route_name: {specialist_pr_auc, general_pr_auc, deficit}}`` for
    every filetype specialist that is *worse* than the general route on its home
    filetype's PR-AUC by more than ``tolerance`` — i.e. ``general - specialist >
    tolerance``. Such a specialist carries no defensible signal: the filetype is
    better served by the general route it falls back to.

    ``tolerance`` is a dead-band, not a required gain: a specialist that ties or
    beats general is always kept, and one that trails by only noise (well within
    eval sampling error) is kept too. This protects strong specialists that are
    statistically tied with an already-excellent general route (e.g. pe at
    0.9986 vs 0.9988) while still dropping genuinely weak ones (e.g. jpeg at
    0.1946 vs 0.2040). The default 0.005 sits in the natural gap observed
    between those two regimes.

    PR-AUC (not ROC-AUC) is the criterion: it is the discriminating metric in
    this rare-positive regime, where a specialist can post a higher ROC-AUC yet
    still be useless at low false-positive rates.
    """
    weak: dict[str, dict[str, float]] = {}
    for ftype, entry in (per_filetype_metrics.get("filetypes") or {}).items():
        if not isinstance(entry, dict):
            continue
        spec = entry.get("specialist")
        gen = entry.get("general")
        if not isinstance(spec, dict) or not isinstance(gen, dict):
            continue  # no same-named specialist for this filetype
        spec_pr = spec.get("pr_auc")
        gen_pr = gen.get("pr_auc")
        if spec_pr is None or gen_pr is None:
            continue
        deficit = float(gen_pr) - float(spec_pr)
        if deficit > tolerance:
            weak[f"filetypes/{ftype}"] = {
                "specialist_pr_auc": float(spec_pr),
                "general_pr_auc": float(gen_pr),
                "deficit": deficit,
            }
    return weak


def _is_blend(obj: Any) -> bool:
    """A learned-blend policy: ``routes`` names paired positionally with a
    float ``weights`` vector (plus ``intercept``/``threshold``). Detected
    structurally so the scrub recurses into it as a unit, not as two
    independent member lists."""
    return (
        isinstance(obj, dict)
        and isinstance(obj.get("routes"), list)
        and isinstance(obj.get("weights"), list)
    )


def _prune_blend(blend: dict[str, Any], drop: frozenset[str]) -> None:
    """Drop ``drop`` routes from a learned blend, removing each route and its
    positionally-aligned weight together. The generic list-scrub below only
    matches *string* members, so on its own it strips a dropped route name out
    of ``routes`` while leaving its float weight in ``weights`` — yielding the
    ``len(weights) == len(routes) + 1`` corruption that makes litmus reject the
    bundle (``blend routes/weights length mismatch``). Nightly retrains routinely
    add/drop specialists, so this lockstep prune is the steady-state path.

    The surviving weights/intercept/threshold are kept as-is: the LR was fit
    jointly so the operating point is now approximate, but dropped routes are
    weak/parity-failed specialists (small marginal contribution) and there's no
    benign/malware data at prune time to honestly recalibrate. A blend that
    loses every route is removed by the caller so the level falls back to its
    OR-rule / single-route policy."""
    routes = blend["routes"]
    weights = blend["weights"]
    if len(routes) != len(weights):
        return  # already malformed; lockstep prune can't realign it
    kept = [(r, w) for r, w in zip(routes, weights) if not (isinstance(r, str) and r in drop)]
    blend["routes"] = [r for r, _ in kept]
    blend["weights"] = [w for _, w in kept]


def _scrub_members(obj: Any, drop: frozenset[str]) -> None:
    """Recursively strip dropped routes used as ensemble *members*: keys in
    threshold maps, elements of ``allowed_routes``/``models`` lists, and a
    ``primary`` scalar that points at a dropped route (reset to ``general``).
    Does NOT touch top-level ``routes`` dict keys — callers scrub policy
    *bodies*, so a filetype's own routing policy survives."""
    if isinstance(obj, dict):
        if _is_blend(obj):
            _prune_blend(obj, drop)
        for key in [k for k in obj if k in drop]:
            del obj[key]
        for key, val in list(obj.items()):
            if key == "primary" and isinstance(val, str) and val in drop:
                obj[key] = "general"
            elif isinstance(val, (dict, list)):
                _scrub_members(val, drop)
                # A blend that lost every route is no longer a policy; drop it so
                # the level falls back to its OR-rule / single-route threshold.
                if _is_blend(val) and not val["routes"]:
                    del obj[key]
    elif isinstance(obj, list):
        obj[:] = [x for x in obj if not (isinstance(x, str) and x in drop)]
        for item in obj:
            if isinstance(item, (dict, list)):
                _scrub_members(item, drop)
        # Drop blends emptied by the recursion above (after pruning, not before).
        obj[:] = [x for x in obj if not (_is_blend(x) and not x["routes"])]


def _prune_config(config: dict[str, Any], drop: frozenset[str]) -> None:
    """Remove dropped routes from ``config.models``. Leaves ``filetype_to_group``
    and ``observed_filetypes`` alone — the filetype still exists and still maps
    to its group; only its dedicated model is gone."""
    config["models"] = [
        m for m in config.get("models", [])
        if not (isinstance(m, dict) and m.get("route") in drop)
    ]


def _prune_route_policies(policy: dict[str, Any], drop: frozenset[str]) -> None:
    for rname, body in (policy.get("routes") or {}).items():
        own_specialist_dropped = rname in drop
        _scrub_members(body, drop)
        if own_specialist_dropped:
            # The filetype's own specialist is gone, so it can no longer be
            # "dominated" by it, and its `primary` must point at a surviving
            # route. Match the specialist-less template (e.g. filetypes/asar:
            # primary "general", dominated_by_specialist false).
            for level in body.get("levels", []):
                best = (level.get("hostile") or {}).get("best") or {}
                if best.get("dominated_by_specialist"):
                    best["dominated_by_specialist"] = False
                if not isinstance(best.get("primary"), str) or best.get("primary") in drop:
                    best["primary"] = "general"


def _prune_per_filetype_metrics(metrics: dict[str, Any], drop: frozenset[str]) -> None:
    def _scrub_entry(entry: Any) -> None:
        if isinstance(entry, dict) and isinstance(entry.get("ensemble_allowed_routes"), list):
            entry["ensemble_allowed_routes"] = [
                r for r in entry["ensemble_allowed_routes"] if r not in drop
            ]

    # `filetypes`/`filegroups` are containers of per-route entries; `all_files`
    # is itself a single entry.
    for section in ("filetypes", "filegroups"):
        block = metrics.get(section)
        if isinstance(block, dict):
            for entry in block.values():
                _scrub_entry(entry)
    _scrub_entry(metrics.get("all_files"))


def referenced_routes(config: dict[str, Any], policy: dict[str, Any]) -> set[str]:
    """Mirror ``validate_azoth_bundle._policy_routes`` + configured routes: the
    full set of routes the bundle validator will demand a model for."""
    routes: set[str] = {"general"}
    for item in config.get("models", []):
        if isinstance(item, dict) and isinstance(item.get("route"), str):
            routes.add(item["route"])
    for _rname, body in (policy.get("routes") or {}).items():
        for level in body.get("levels", []):
            best = (level.get("hostile") or {}).get("best") or {}
            thresholds = best.get("thresholds") or {}
            routes.update(str(name) for name in thresholds)
    return routes


def prune_routes(azoth_root: Path, drop_routes: set[str]) -> set[str]:
    """Drop ``drop_routes`` from the bundle at ``azoth_root``: rewrite
    ``config.json``, ``route_policies.json`` and ``per_filetype_metrics.json``,
    and remove the route directories. Idempotent. Returns the routes actually
    pruned (present in the bundle and not protected).

    Raises ``ValueError`` if a protected route is requested, or if a referenced
    route would survive in config/policies after pruning (the same invariant
    the deploy-time bundle validator enforces)."""
    bad = drop_routes & PROTECTED_ROUTES
    if bad:
        raise ValueError(f"refusing to prune protected route(s): {sorted(bad)}")
    drop = frozenset(drop_routes)
    if not drop:
        return set()

    config_path = azoth_root / "config.json"
    policy_path = azoth_root / "route_policies.json"
    metrics_path = azoth_root / "per_filetype_metrics.json"

    config = json.loads(config_path.read_text())
    policy = json.loads(policy_path.read_text())

    _prune_config(config, drop)
    _prune_route_policies(policy, drop)

    # Invariant check BEFORE writing: nothing the validator inspects may still
    # demand a model for a dropped route.
    survivors = referenced_routes(config, policy) & drop
    if survivors:
        raise ValueError(
            f"prune left dangling references to {sorted(survivors)}; aborting "
            f"without writing (bundle would fail validation)"
        )

    config_path.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    policy_path.write_text(json.dumps(policy, indent=2, ensure_ascii=False) + "\n")
    if metrics_path.is_file():
        metrics = json.loads(metrics_path.read_text())
        _prune_per_filetype_metrics(metrics, drop)
        metrics_path.write_text(json.dumps(metrics, indent=2, ensure_ascii=False) + "\n")

    pruned: set[str] = set()
    for route in drop:
        route_dir = azoth_root / route
        if route_dir.is_dir():
            shutil.rmtree(route_dir)
        pruned.add(route)
    return pruned
