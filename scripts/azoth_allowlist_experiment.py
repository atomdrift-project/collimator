#!/usr/bin/env python3
"""Fast experiment kernel for the global-allowlist 'virtual route'.

autocollie drives this: sweep --level, rank by (allowlist size = memory) subject
to (no proxy route's recall@1e-3 regresses). Extraction is cached on --prepare so
each --level run is just refit+score → fits the ≤10-min experiment budget.

  prepare (once):  importance set (deployed bundle ONNX), corpus freq array,
                   and per-proxy-route matrices (extracted at each route's spec).
  per level:       allowlist = importance ∪ top-N corpus-frequency; per route,
                   keep the columns whose feature NAME is in the allowlist; fit
                   full vs pruned; emit JSON {feats, dRecall@1e-3, dAUC}.

The inner loop screens memory + COARSE quality only — it cannot resolve L50
(tail needs OOF benign volume). The winning level is tail-validated by the ~1h
finalize train and the 8h deploy gate (check_azoth_regression.py).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from pathlib import Path

import numpy as np
import scipy.sparse as sp

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import scripts.azoth_specialist_suite as S
from collimator import features as F
from collimator.model import create_classifier, predict_proba

CORPUS_TYPES = ["pe","xml","java_class","png","javascript","c","go","csharp","html",
                "json","rust","pdf","shell","elf","python","macho","ruby","perl","php"]
CACHE = Path("out/allowlist_exp")
PARAMS = dict(n_estimators=150, max_depth=12, learning_rate=0.05, num_leaves=96,
              min_child_samples=100, learner="azoth", device="cpu", num_threads=8)


def _resolve(route, bundle):
    if route == "general":
        return list(CORPUS_TYPES), os.path.join(bundle, "general/feature_spec.json")
    if route in S.DEPLOYMENT_GROUPS:
        return list(S.DEPLOYMENT_GROUPS[route]), os.path.join(bundle, f"filegroups/{route}/feature_spec.json")
    p = os.path.join(bundle, f"filetypes/{route}/feature_spec.json")
    if not os.path.exists(p): p = os.path.join(bundle, "general/feature_spec.json")
    return [route], p


def _fetch(file_types, cap):
    tr, te = [], []
    for ft in file_types:
        rows = S._fetch_rows(S_DSN, file_types=(ft,), max_id=0, min_score=None)
        tr += S._ids_labels(rows, test=False); te += S._ids_labels(rows, test=True)
    rng = np.random.default_rng(0)
    if cap and len(tr) > cap: tr = [tr[i] for i in rng.choice(len(tr), cap, replace=False)]
    if len(te) > cap: te = [te[i] for i in rng.choice(len(te), cap, replace=False)]
    return tr, te


def _used_names(onnx_path, names):
    import onnx
    m = onnx.load(onnx_path); ids = modes = None
    for n in m.graph.node:
        for a in n.attribute:
            if a.name == "nodes_featureids": ids = list(a.ints)
            if a.name == "nodes_modes": modes = [s.decode() if isinstance(s, bytes) else s for s in a.strings]
    if ids is None: return set()
    pairs = zip(ids, modes) if modes else ((i, "X") for i in ids)
    return {names[i] for i, md in pairs if md != "LEAF" and 0 <= i < len(names)}


def prepare(bundle, routes, cap, workers):
    CACHE.mkdir(parents=True, exist_ok=True)
    gspec = F.FeatureSpec.load(os.path.join(bundle, "general/feature_spec.json"))
    gnames = list(gspec.feature_names)
    # importance across all deployed route models (mapped via each route's spec)
    imp = set(); nmod = 0
    for op in glob.glob(os.path.join(bundle, "**/models/*.onnx"), recursive=True):
        sp_ = os.path.join(os.path.dirname(os.path.dirname(op)), "feature_spec.json")
        nm = list(F.FeatureSpec.load(sp_).feature_names) if os.path.exists(sp_) else gnames
        imp |= _used_names(op, nm); nmod += 1
    imp &= set(gnames)
    # corpus frequency (general-spec name space)
    rng = np.random.default_rng(1); samp = []
    for ft in CORPUS_TYPES:
        tr = S._ids_labels(S._fetch_rows(S_DSN, file_types=(ft,), max_id=0, min_score=None), test=False)
        if tr: samp += [tr[i] for i in rng.choice(len(tr), min(4000, len(tr)), replace=False)]
    Xc, _, _, _ = F.extract_partitioned_from_db(S_DSN, samp, [], gspec, n_workers=workers)
    freq = np.asarray((Xc > 0).sum(axis=0)).ravel(); del Xc
    json.dump({"importance": sorted(imp), "gnames": gnames}, open(CACHE / "meta.json", "w"))
    np.save(CACHE / "freq.npy", freq)
    print(f"[prepare] importance={len(imp)} across {nmod} models; freq computed", flush=True)
    for r in routes:
        fts, spath = _resolve(r, bundle)
        rspec = F.FeatureSpec.load(spath); rnames = list(rspec.feature_names)
        tr, te = _fetch(fts, cap)
        Xtr, ytr, Xte, yte = F.extract_partitioned_from_db(S_DSN, tr, te, rspec, n_workers=workers)
        sp.save_npz(CACHE / f"{r}_Xtr.npz", Xtr); sp.save_npz(CACHE / f"{r}_Xte.npz", Xte)
        np.savez(CACHE / f"{r}_y.npz", ytr=ytr, yte=yte)
        json.dump(rnames, open(CACHE / f"{r}_names.json", "w"))
        print(f"[prepare] {r}: Xtr{Xtr.shape} nnz={Xtr.nnz:,} test_benign={int((yte==0).sum())} mal={int((yte==1).sum())}", flush=True)


def _recall_at(p, y, frac):
    bs = np.sort(p[y == 0])[::-1]; nb = len(bs)
    thr = bs[min(max(1, int(frac * nb)), nb - 1)]
    return float((p[y == 1] >= thr).mean())


def _allow_for_level(level):
    """importance ∪ top-(level - |importance|) corpus-frequency feature names."""
    meta = json.load(open(CACHE / "meta.json")); imp = set(meta["importance"]); gnames = meta["gnames"]
    freq = np.load(CACHE / "freq.npy")
    order = np.argsort(-freq)
    floor = {gnames[i] for i in order[freq[order] > 0][:max(0, level - len(imp))]}
    return imp | floor


def _score(routes, allow, label):
    """Fit full-vs-pruned per proxy route for an explicit allowlist name set."""
    from sklearn.metrics import roc_auc_score
    out = {**label, "allowlist_size": len(allow), "routes": {}}
    for r in routes:
        Xtr = sp.load_npz(CACHE / f"{r}_Xtr.npz").tocsr(); Xte = sp.load_npz(CACHE / f"{r}_Xte.npz").tocsr()
        yz = np.load(CACHE / f"{r}_y.npz"); ytr, yte = yz["ytr"], yz["yte"]
        rnames = json.load(open(CACHE / f"{r}_names.json"))
        keep = np.array([i for i, nm in enumerate(rnames) if nm in allow])
        rec = {}
        for tag, X in [("full", (Xtr, Xte)), ("pruned", (Xtr[:, keep], Xte[:, keep]))]:
            Xa, Xb = X
            m = create_classifier(n_benign=int((ytr == 0).sum()), n_malware=int((ytr == 1).sum()),
                                  n_rows=Xa.shape[0], n_features=Xa.shape[1], nnz=Xa.nnz, **PARAMS)
            m.fit(Xa, ytr); p = predict_proba(m, Xb)
            rec[tag] = {"feats": int(Xa.shape[1]), "auc": round(float(roc_auc_score(yte, p)), 4),
                        "r1e3": round(_recall_at(p, yte, 1e-3), 4)}
        rec["d_r1e3"] = round(rec["pruned"]["r1e3"] - rec["full"]["r1e3"], 4)
        rec["d_auc"] = round(rec["pruned"]["auc"] - rec["full"]["auc"], 4)
        out["routes"][r] = rec
        print(f"  {r:8} feats {rec['full']['feats']}->{rec['pruned']['feats']} "
              f"R@1e-3 {rec['full']['r1e3']:.4f}->{rec['pruned']['r1e3']:.4f} (d={rec['d_r1e3']:+.4f}) "
              f"dAUC={rec['d_auc']:+.4f}", flush=True)
    out["worst_d_r1e3"] = round(min(v["d_r1e3"] for v in out["routes"].values()), 4)
    out["mem_proxy_feats"] = len(allow)
    print(f"  >>> {label} allowlist={len(allow)} worst_dR@1e-3={out['worst_d_r1e3']:+.4f}", flush=True)
    return out


def run_level(routes, level):
    return _score(routes, _allow_for_level(level), {"level": level})


def _load_allowlist_names(path):
    d = json.load(open(path))
    return set(d if isinstance(d, list) else d.get("significant_features", []))


def _write_allowlist(names, path, extra_meta):
    full = len(json.load(open(CACHE / "meta.json"))["gnames"])
    out = {"significant_features": sorted(names),
           "meta": {"kept": len(names), "full": full, "drop_pct": round(100 * (full - len(names)) / full, 1),
                    **extra_meta}}
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    json.dump(out, open(path, "w"), indent=0)


def tune(routes, levels, tolerance, out_path):
    """Sweep levels, pick the SMALLEST allowlist whose worst_dR@1e-3 >= tolerance,
    and (optionally) write its allowlist as a candidate pin. The 'virtual route'
    experiment autocollie drives — recommends a candidate; promotion stays gated."""
    scored = []
    for lvl in sorted(levels):
        r = run_level(routes, lvl)
        scored.append((r["allowlist_size"], lvl, r["worst_d_r1e3"]))
    passing = [s for s in scored if s[2] >= tolerance]
    pick = min(passing) if passing else min(scored, key=lambda s: (-s[2], s[0]))  # fallback: least-bad
    size, lvl, worst = pick
    if out_path:
        _write_allowlist(_allow_for_level(lvl), out_path,
                         {"tuned_level": lvl, "proxy_worst_dR_1e3": worst, "tolerance": tolerance,
                          "routes": routes, "note": "candidate pin from azoth_allowlist_experiment --tune; adopt via check_azoth_regression"})
    print(f"\nTUNE recommend level={lvl} size={size} worst_dR@1e-3={worst:+.4f} "
          f"(tol={tolerance:+.3f}, {'PASS' if worst >= tolerance else 'NO PASS - least-bad'})"
          + (f" -> wrote {out_path}" if out_path else ""))
    return {"recommended_level": lvl, "recommended_size": size, "worst_d_r1e3": worst, "swept": scored}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--bundle", default=os.path.expanduser("~/azoth"))
    ap.add_argument("--db", default=os.environ.get("DB", "postgres://hopper@localhost:5432/hopper"))
    ap.add_argument("--routes", default="general,elf,source")
    ap.add_argument("--cap", type=int, default=120000)
    ap.add_argument("--workers", type=int, default=16)
    ap.add_argument("--prepare", action="store_true")
    ap.add_argument("--level", type=int, default=None)
    ap.add_argument("--committed", default=None,
                    help="score this committed allowlist file (the current pin) on the proxy routes")
    ap.add_argument("--tune", default=None,
                    help="comma-separated levels to sweep; recommends + writes the smallest passing one")
    ap.add_argument("--tolerance", type=float, default=-0.01,
                    help="worst_dR@1e-3 floor: monitor 're-tune' threshold / tune accept threshold")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    global S_DSN; S_DSN = a.db
    routes = [r.strip() for r in a.routes.split(",") if r.strip()]
    if a.prepare: prepare(a.bundle, routes, a.cap, a.workers)
    if a.committed is not None:
        res = _score(routes, _load_allowlist_names(a.committed), {"committed": a.committed})
        verdict = "OK" if res["worst_d_r1e3"] >= a.tolerance else "RE-TUNE (committed pin regresses proxy)"
        if a.out: json.dump(res, open(a.out, "w"), indent=2)
        print(f"\nMONITOR committed={a.committed} size={res['allowlist_size']} "
              f"worst_dR@1e-3={res['worst_d_r1e3']:+.4f} tol={a.tolerance:+.3f} -> {verdict}")
    if a.tune is not None:
        levels = [int(x) for x in a.tune.split(",") if x.strip()]
        tune(routes, levels, a.tolerance, a.out)
    if a.level is not None:
        res = run_level(routes, a.level)
        if a.out: json.dump(res, open(a.out, "w"), indent=2)
        print("\nSCORE " + json.dumps({k: res[k] for k in ("level", "allowlist_size", "worst_d_r1e3")}))


if __name__ == "__main__":
    main()
