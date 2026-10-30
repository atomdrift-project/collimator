#!/usr/bin/env python3
"""Rerun matched controls after explicitly excluding malformed training rows."""
import argparse
import json
import os
from pathlib import Path
import sqlite3
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from keyword_route_controls import VARIANTS, command, paired_changes, read_variant


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-db", default="postgres://hopper@localhost:5432/hopper")
    parser.add_argument("--study", type=Path, default=Path("out/experiments/keyword-controls-10pct-confirm"))
    parser.add_argument("--route", default="go")
    args = parser.parse_args()
    os.environ["COLLIMATOR_SAMPLE_PERCENT"] = "10"
    os.environ["EXP_EVAL_SEED"] = "42"
    from collimator import data
    from collimator.bundle import atomic_write_json
    from collimator.corpus_snapshot import frozen_corpus
    source = args.study / args.route
    audit = json.loads((source / "missing_descriptions.json").read_text())
    if any(row["partition"] != "train" for row in audit["affected_rows"]):
        raise ValueError("dev exclusions require a new study; refusing to change this dev cohort")
    excluded = {row["row_id"] for row in audit["affected_rows"]}
    if len(excluded) != 1:
        raise ValueError("this repair is scoped to the single audited malformed training row")
    cohort = json.loads((source / "selected_cohort.json").read_text())
    selected = {row["row_id"]: row for key in ("train", "test") for row in cohort[key] if row["row_id"] not in excluded}
    directory = args.study / f"{args.route}-clean"
    directory.mkdir(exist_ok=True)
    database = directory / "cohort.db"
    if database.exists():
        raise ValueError("filtered cohort already exists; use a fresh study directory")
    columns = "id,sha256,path,label,canonical_sha256,cleave_result,formula,elements,score,mtime,file_type,skip"
    manifest = dict(excluded_training_rows=sorted(excluded),
                    reason="Missing required trait description; same exclusion applied to all four training arms.",
                    dev_exclusions=[], source=str(source / "selected_cohort.json"),
                    scope="Private copy of the saved 10% train/dev row selection; live corpus unchanged.")
    with frozen_corpus(args.source_db), sqlite3.connect(database) as target:
        target.execute("CREATE TABLE samples (id INTEGER PRIMARY KEY, sha256 TEXT, path TEXT, label TEXT, canonical_sha256 TEXT, cleave_result TEXT, formula TEXT, elements TEXT, score INTEGER, mtime TEXT, file_type TEXT, skip TEXT)")
        with data._connect(args.source_db) as connection:
            ids = sorted(selected)
            copied = 0
            for start in range(0, len(ids), 500):
                cursor = connection.execute(f"SELECT {columns} FROM samples WHERE id = ANY(%s) ORDER BY id", (ids[start:start + 500],))
                for row in cursor:
                    values = list(row)
                    expected = selected[values[0]]
                    if data._label_int(values[3]) != expected["label"] or values[4] != expected["group_id"] or values[-1]:
                        raise ValueError("selected row identity/eligibility changed before export")
                    if not isinstance(values[5], str):
                        values[5] = json.dumps(values[5])
                    values[9] = str(values[9]) if values[9] is not None else ""
                    target.execute("INSERT INTO samples VALUES (?,?,?,?,?,?,?,?,?,?,?,?)", values)
                    copied += 1
            if copied != len(selected):
                raise ValueError("some selected rows were deleted")
        target.create_function("md5", 1, lambda text: __import__("hashlib").md5(text.encode()).hexdigest())
        if target.execute(f"SELECT count(*) FROM samples WHERE {data.sample_predicate('10')}").fetchone()[0] != copied:
            raise ValueError("export contains rows outside the requested 10% hash cohort")
        manifest["copied_rows"] = copied
    for key in ("train", "test"):
        cohort[key] = [row for row in cohort[key] if row["row_id"] not in excluded]
    # Route controls are for one filetype, so the removed training row has
    # one corresponding primary-filetype entry in this parallel array.
    original = json.loads((source / "selected_cohort.json").read_text())
    cohort["train_file_types"] = [ft for row, ft in zip(original["train"], original["train_file_types"], strict=True)
                                  if row["row_id"] not in excluded]
    atomic_write_json(directory / "selected_cohort.json", cohort)
    atomic_write_json(directory / "exclusions.json", manifest)
    print(f"Exported {manifest['copied_rows']} train/dev rows; excluded {sorted(excluded)} from train only", flush=True)
    study = dict(manifest=manifest, variants={})
    controls = argparse.Namespace(db=str(database.resolve()), seed=43, trees=180)
    identity = None
    for variant in VARIANTS:
        print(f"Starting {args.route}-clean/{variant}", flush=True)
        with (directory / f"{variant}.log").open("w") as log:
            subprocess.run(command(controls, args.route, variant, directory), env=os.environ.copy(),
                           stdout=log, stderr=subprocess.STDOUT, check=True)
        result, captured = read_variant(directory / variant, directory / "cache", 43)
        if identity is None:
            identity = captured
        if captured != identity:
            raise ValueError("clean comparison inputs differ")
        if variant != "baseline":
            paired_changes(directory, study["variants"]["baseline"], variant, result)
        study["variants"][variant] = result
        result["verified_matched_inputs"] = True
        atomic_write_json(directory / "comparison.json", study)
        print(json.dumps(dict(variant=variant, recalls=[(r["seed"], r["recall_at_0fp"], r["recall_at_1fp"]) for r in result["seeds"]])), flush=True)


if __name__ == "__main__":
    main()
