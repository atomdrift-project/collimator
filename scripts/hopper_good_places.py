"""Repair manifest support for files independently observed in good locations.

Planning is read-only. Locations within one parent count once, and dependency
references do not establish that the referenced bytes occur in a good package.
"""

import argparse
import hashlib
import json
import os
import threading
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from itertools import islice

import psycopg
from psycopg.rows import dict_row


PLAN_SQL = """
SELECT s.sha256, s.label, s.label_source, s.skip, s.path, s.parent,
       s.file_type, s.cleave_result IS NOT NULL AS analyzed,
       s.updated_at, COALESCE(e.places, '[]'::jsonb) AS places,
       COALESCE(b.locations, '[]'::jsonb) AS bad_locations
FROM unnest(%s::text[]) AS wanted(sha256)
JOIN samples s USING (sha256)
LEFT JOIN LATERAL (
    SELECT jsonb_agg(place) AS places FROM (
      (SELECT 'path' AS kind, l.path AS identity, l.id AS location_id,
              l.path, l.parent_sha256, l.rel
       FROM sample_locations l
       WHERE l.sha256=s.sha256 AND l.parent_sha256='' AND l.path LIKE 'good/%%'
       LIMIT 2)
      UNION ALL
      (SELECT DISTINCT ON (l.parent_sha256)
              'parent' AS kind, l.parent_sha256 AS identity,
              l.id AS location_id, l.path, l.parent_sha256, l.rel
       FROM sample_locations l
       WHERE l.sha256=s.sha256 AND l.parent_sha256<>'' AND l.rel IN ('','unpacked')
         AND NOT (l.path LIKE 'bad/%%' AND position('!!' in l.path)=0)
         AND EXISTS (SELECT 1 FROM samples p
                     WHERE p.sha256=l.parent_sha256 AND p.label='good')
       ORDER BY l.parent_sha256, l.id DESC LIMIT 2)
      LIMIT 2
    ) place
) e ON s.label='bad'
LEFT JOIN LATERAL (
    SELECT jsonb_agg(jsonb_build_object(
        'id', l.id, 'path', l.path, 'parent_sha256', l.parent_sha256, 'rel', l.rel
    )) AS locations
    FROM (
        SELECT id, path, parent_sha256, rel FROM sample_locations
        WHERE sha256=s.sha256 AND parent_sha256='' AND path COLLATE "C" LIKE 'bad/%%'
          AND position('!!' in path)=0
        UNION ALL
        SELECT id, path, parent_sha256, rel FROM sample_locations
        WHERE sha256=s.sha256 AND parent_sha256<>'' AND path LIKE 'bad/%%'
          AND position('!!' in s.path)=0 AND position('!!' in path)=0
    ) l
) b ON s.label='bad' AND jsonb_array_length(e.places)>=2
"""


def eligible(row):
    return row["label"] == "bad" and len({(p["kind"], p["identity"]) for p in row["places"]}) >= 2


def ambiguous_place(place):
    return place["kind"] == "parent" and place["path"].startswith("bad/") and "!!" not in place["path"]


def refine(args):
    """Replace ambiguous legacy witnesses before the first write, retaining the original plan."""
    out = Path(args.output)
    summary = json.loads((out / "plan_summary.json").read_text())
    if summary["status"] != "complete" or (out / "apply.jsonl").exists():
        raise ValueError("Refine requires a complete, unapplied plan")
    if (out / "plan.original.jsonl").exists():
        raise ValueError("Plan has already been refined")
    replacements = {}
    wanted = [r["sha256"] for r in records(out / "plan.jsonl") if any(ambiguous_place(p) for p in r["places"])]
    with psycopg.connect(args.db, autocommit=True, row_factory=dict_row,
        application_name="good-places-refine", options="-c default_transaction_read_only=on -c statement_timeout=600000") as conn:
        for start in range(0, len(wanted), 100):
            for row in conn.execute(PLAN_SQL, (wanted[start:start+100],)):
                row["eligible"] = eligible(row)
                replacements[row["sha256"]] = row
    if len(replacements) != len(wanted):
        raise ValueError("A candidate disappeared during refinement")
    counts = Counter()
    with (out / "plan.refined.jsonl").open("x") as dest:
        for old in records(out / "plan.jsonl"):
            row = replacements.get(old["sha256"], old)
            counts["requested"] += 1
            counts["eligible" if row["eligible"] else "ineligible"] += 1
            if row["eligible"]:
                counts["bad_locations"] += len(row["bad_locations"])
                counts["legacy_bad_locations"] += sum(bool(l["parent_sha256"]) for l in row["bad_locations"])
                counts["files_with_bad_locations"] += bool(row["bad_locations"])
            dest.write(json.dumps(row, default=str)+"\n")
        dest.flush()
        os.fsync(dest.fileno())
    (out / "plan.jsonl").rename(out / "plan.original.jsonl")
    (out / "plan.refined.jsonl").rename(out / "plan.jsonl")
    summary = {"status": "complete", **counts, "refined_legacy_evidence": len(wanted)}
    (out / "plan_summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    print(json.dumps(summary), flush=True)


def records(path):
    with Path(path).open() as source:
        for line in source:
            yield json.loads(line)


def journal(dest, value):
    dest.write(json.dumps(value, default=str) + "\n")
    dest.flush()
    os.fsync(dest.fileno())


def apply_batch(conn, rows, source):
    """Recheck the original witnesses and change labels and audit atomically.

    Lock good parents and their exact locations before the candidate rows. Newly
    corrected files cannot become evidence: only the saved witnesses are used.
    """
    wanted = {r["sha256"]: r for r in rows if r["eligible"]}
    if not wanted:
        return {}
    places = [p for r in wanted.values() for p in r["places"]]
    parents = sorted({p["parent_sha256"] for p in places if p["kind"] == "parent"})
    with conn.transaction():
        good = {r["sha256"] for r in conn.execute(
            "SELECT sha256 FROM samples WHERE sha256=ANY(%s) AND label='good' ORDER BY sha256 FOR SHARE",
            (parents,),
        )}
        locations = {r["id"]: r for r in conn.execute(
            "SELECT id,sha256,path,parent_sha256,rel FROM sample_locations WHERE id=ANY(%s) ORDER BY id FOR SHARE",
            (sorted({p["location_id"] for p in places}),),
        )}
        current = conn.execute(
            "SELECT sha256,label,label_source,skip,path FROM samples WHERE sha256=ANY(%s) ORDER BY sha256 FOR UPDATE",
            (sorted(wanted),),
        ).fetchall()
        result = dict.fromkeys(wanted, "missing")
        updates = []
        for row in current:
            sha = row["sha256"]
            old = wanted[sha]
            if row["label"] == "good" and row["label_source"] == source:
                result[sha] = "already_applied"
                continue
            # The preferred path changes during routine walks. We do not write
            # it, and eligibility rests on locked exact witness locations.
            if any(row[k] != old[k] for k in ("label", "label_source", "skip")):
                result[sha] = "changed_since_plan"
                continue
            evidence = set()
            for p in old["places"]:
                if ambiguous_place(p):
                    continue
                loc = locations.get(p["location_id"])
                if not loc or loc["sha256"] != sha or any(loc[k] != p[k] for k in ("path", "parent_sha256", "rel")):
                    continue
                if p["kind"] == "path" and not loc["parent_sha256"] and loc["path"].startswith("good/"):
                    evidence.add(("path", loc["path"]))
                elif p["kind"] == "parent" and loc["rel"] in ("", "unpacked") and loc["parent_sha256"] in good:
                    evidence.add(("parent", loc["parent_sha256"]))
            if len(evidence) < 2:
                result[sha] = "lost_evidence"
                continue
            updates.append(sha)
            result[sha] = "applied"
        if updates:
            conn.execute("""
                WITH changed AS (
                    UPDATE samples SET label='good', label_source=%s, updated_at=now()
                    WHERE sha256=ANY(%s) RETURNING sha256, skip
                )
                INSERT INTO label_events (sha256,from_label,to_label,from_skip,to_skip,reason)
                SELECT sha256,'bad','good',skip,skip,%s FROM changed
            """, (source, updates, source))
    return result


def apply(args):
    out = Path(args.output)
    if json.loads((out / "plan_summary.json").read_text())["status"] != "complete":
        raise ValueError("Planning must finish before applying")
    # The plan is the durable preimage, including skips and original sources.
    with (out / "plan.jsonl").open() as preimage:
        os.fsync(preimage.fileno())
    counts = Counter()
    with psycopg.connect(args.db, autocommit=True, row_factory=dict_row,
                          application_name="good-places-apply",
                          options="-c lock_timeout=10000 -c statement_timeout=60000") as conn, \
            (out / "apply.jsonl").open("a") as log:
        source = iter(records(out / "plan.jsonl"))
        while batch := list(islice(source, 200)):
            result = apply_batch(conn, batch, args.source)
            journal(log, {"result": result})
            counts.update(result.values())
            if sum(counts.values()) % 10000 < 200:
                print(json.dumps(dict(counts)), flush=True)
    (out / "apply_summary.json").write_text(json.dumps(dict(counts), indent=2)+"\n")
    print(json.dumps(dict(counts)), flush=True)


def move_request(sha, path, source):
    return {"verdicts": [{"sha256": sha, "old_path": path, "ruling": "good", "source": source}]}


class HopperAPI:
    def __init__(self, url, token_path):
        self.url = url.rstrip("/")
        token = next(line.strip() for line in Path(token_path).expanduser().read_text().splitlines() if line.strip())
        self.headers = {"Authorization": "Bearer " + token, "Sec-Fetch-Site": "same-origin"}

    def hash_path(self, path):
        req = urllib.request.Request(self.url + "/data/" + urllib.parse.quote(path), headers=self.headers)
        digest = hashlib.sha256()
        with urllib.request.urlopen(req, timeout=120) as response:
            while chunk := response.read(1024 * 1024):
                digest.update(chunk)
        return digest.hexdigest()

    def move(self, sha, path, source):
        req = urllib.request.Request(self.url + "/api/triage",
            data=json.dumps(move_request(sha, path, source)).encode(),
            headers={**self.headers, "Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=300) as response:
            result = json.load(response)["results"]
        if len(result) != 1 or result[0]["sha256"] != sha:
            raise ValueError("Unexpected triage response")
        return result[0]


def preserve_skip(conn, row, source):
    """An API cache hit can relabel again and clear skip; restore only our write.

    The on-disk plan survives a client crash between the API write and this
    restoration. Resuming moves repeats this step even for completed moves.
    """
    with conn.transaction():
        current = conn.execute("SELECT label,label_source,skip FROM samples WHERE sha256=%s FOR UPDATE",
                               (row["sha256"],)).fetchone()
        if current["label"] != "good" or current["label_source"] != source:
            return "label_changed"
        if current["skip"] == row["skip"]:
            return "preserved"
        if current["skip"]:
            return "skip_changed"
        conn.execute("UPDATE samples SET skip=%s,skipped_at=%s,updated_at=now() WHERE sha256=%s",
                     (row["skip"], row["skipped_at"], row["sha256"]))
        conn.execute("""INSERT INTO label_events (sha256,from_label,to_label,from_skip,to_skip,reason)
                        VALUES (%s,'good','good','',%s,%s)""",
                     (row["sha256"], row["skip"], source+":preserve-skip"))
        return "restored"


def normalize_location(conn, sha, loc):
    """Only call after the API has proven the exact physical path's SHA."""
    with conn.transaction():
        changed = conn.execute("""UPDATE sample_locations SET parent_sha256='',rel=''
            WHERE id=%s AND sha256=%s AND path=%s AND parent_sha256=%s AND rel=%s RETURNING id""",
            (loc["id"], sha, loc["path"], loc["parent_sha256"], loc["rel"])).fetchone()
        return bool(changed)


def move(args):
    out = Path(args.output)
    if not (out / "apply_summary.json").exists():
        raise ValueError("Apply must finish before moving")
    api = HopperAPI(args.api, args.token)
    completed = set()
    skip_times = {}
    log_path = out / "moves.jsonl"
    if log_path.exists():
        for record in records(log_path):
            if "skipped_at" in record:
                skip_times[record["sha256"]] = record["skipped_at"]
            if record.get("result", {}).get("source_removed"):
                completed.add((record["sha256"], record["path"]))
    counts = Counter()
    lock = threading.Lock()
    local = threading.local()
    connections = []
    with log_path.open("a") as log:
        def record(value):
            with lock:
                journal(log, value)

        def relocate(row):
            if not hasattr(local, "conn"):
                local.conn = psycopg.connect(args.db, autocommit=True, row_factory=dict_row,
                    application_name="good-places-move", options="-c lock_timeout=10000 -c statement_timeout=60000")
                with lock:
                    connections.append(local.conn)
            conn = local.conn
            sha = row["sha256"]
            current = conn.execute("SELECT label,label_source,skip,skipped_at FROM samples WHERE sha256=%s", (sha,)).fetchone()
            if not current or current["label"] != "good" or current["label_source"] != args.source:
                return Counter({"not_ours": 1})
            if sha not in skip_times:
                if current["skip"] != row["skip"]:
                    return Counter({"skip_changed": 1})
                record({"sha256": sha, "skipped_at": current["skipped_at"]})
            row["skipped_at"] = skip_times.get(sha, current["skipped_at"])
            outcomes = Counter()
            for loc in row["bad_locations"]:
                path = loc["path"]
                try:
                    if (sha, path) in completed:
                        outcomes["already_moved"] += 1
                        continue
                    if loc["parent_sha256"]:
                        current_loc = conn.execute("SELECT parent_sha256,rel FROM sample_locations WHERE id=%s", (loc["id"],)).fetchone()
                        if current_loc and current_loc["parent_sha256"]:
                            if current_loc != {"parent_sha256": loc["parent_sha256"], "rel": loc["rel"]}:
                                raise ValueError("Location relationship changed since planning")
                            digest = api.hash_path(path)
                            if digest != sha:
                                raise ValueError("Physical source SHA does not match catalog")
                            # Persist the old relationship before its bounded CAS.
                            record({"sha256": sha, "path": path, "normalizing": loc, "verified_sha256": digest})
                            if not normalize_location(conn, sha, loc):
                                raise ValueError("Location changed during normalization")
                    result = api.move(sha, path, args.source)
                    record({"sha256": sha, "path": path, "result": result})
                    outcomes[result["status"]] += 1
                except Exception as exc:
                    record({"sha256": sha, "path": path, "error": str(exc)})
                    outcomes["error"] += 1
                finally:
                    skip = preserve_skip(conn, row, args.source)
                    if skip != "preserved":
                        record({"sha256": sha, "skip_status": skip})
                        outcomes["skip_" + skip] += 1
            return outcomes

        try:
            with ThreadPoolExecutor(args.workers) as pool:
                source = (r for r in records(out / "plan.jsonl") if r["eligible"] and r["bad_locations"])
                while batch := list(islice(source, 100)):
                    for result in pool.map(relocate, batch):
                        counts.update(result)
                    (out / "move_summary.json").write_text(json.dumps({"status": "running", **counts}, indent=2)+"\n")
                    print(json.dumps(dict(counts)), flush=True)
            (out / "move_summary.json").write_text(json.dumps({"status": "complete", **counts}, indent=2)+"\n")
        finally:
            for conn in connections:
                conn.close()


def verify(args):
    out = Path(args.output)
    counts = Counter()
    types = {}
    with psycopg.connect(args.db, autocommit=True, row_factory=dict_row,
        application_name="good-places-verify", options="-c default_transaction_read_only=on -c statement_timeout=60000") as conn, \
            (out / "verification_details.jsonl").open("w") as details:
        source = iter(records(out / "plan.jsonl"))
        while batch := list(islice(source, 1000)):
            actual = {r["sha256"]: r for r in conn.execute(
                "SELECT sha256,label,label_source,skip,file_type,cleave_result IS NOT NULL AS analyzed FROM samples WHERE sha256=ANY(%s)",
                ([r["sha256"] for r in batch],))}
            for old in batch:
                row = actual.get(old["sha256"])
                if not row:
                    counts["missing"] += 1
                    continue
                ours = row["label"] == "good" and row["label_source"] == args.source
                status = "corrected" if ours else row["label"]
                counts[status] += 1
                by_type = types.setdefault(row["file_type"], Counter())
                by_type[status] += 1
                if ours:
                    if row["skip"] != old["skip"]:
                        counts["changed_skip"] += 1
                    if row["analyzed"] and not row["skip"]:
                        counts["corrected_analyzed_unskipped"] += 1
                        by_type["corrected_analyzed_unskipped"] += 1
                if not ours or row["skip"] != old["skip"]:
                    details.write(json.dumps({"sha256": row["sha256"], "eligible": old["eligible"],
                        "current": row, "original_skip": old["skip"]})+"\n")
    summary = {"counts": counts, "by_type": types}
    (out / "verification_summary.json").write_text(json.dumps(summary, indent=2)+"\n")
    print(json.dumps(summary), flush=True)


def read_manifest(path):
    seen = set()
    with Path(path).open() as source:
        for line in source:
            sha = json.loads(line)["sha256"]
            if len(sha) != 64 or any(c not in "0123456789abcdef" for c in sha):
                raise ValueError(f"Invalid SHA-256: {sha!r}")
            if sha in seen:
                raise ValueError(f"Duplicate SHA-256: {sha}")
            seen.add(sha)
            yield sha


def plan(args):
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    local = threading.local()
    connections = []
    lock = threading.Lock()
    counts = Counter()

    def inspect(shas):
        if not hasattr(local, "conn"):
            local.conn = psycopg.connect(
                args.db, row_factory=dict_row, autocommit=True,
                application_name="good-places-plan",
                options="-c default_transaction_read_only=on -c statement_timeout=600000",
            )
            with lock:
                connections.append(local.conn)
        return local.conn.execute(PLAN_SQL, (sorted(shas),)).fetchall()

    try:
        with (out / "plan.jsonl").open("x") as dest, ThreadPoolExecutor(args.workers) as pool:
            source = iter(read_manifest(args.manifest))
            while True:
                chunk = []
                for _ in range(args.workers * 500):
                    sha = next(source, None)
                    if sha is None:
                        break
                    chunk.append(sha)
                if not chunk:
                    break
                batches = [chunk[i:i+500] for i in range(0, len(chunk), 500)]
                for batch, rows in zip(batches, pool.map(inspect, batches)):
                    counts["requested"] += len(batch)
                    counts["missing"] += len(batch) - len(rows)
                    for row in rows:
                        row["eligible"] = eligible(row)
                        counts["eligible" if row["eligible"] else "ineligible"] += 1
                        if row["eligible"]:
                            counts["bad_locations"] += len(row["bad_locations"])
                            counts["legacy_bad_locations"] += sum(bool(l["parent_sha256"]) for l in row["bad_locations"])
                            counts["files_with_bad_locations"] += bool(row["bad_locations"])
                        dest.write(json.dumps(row, default=str) + "\n")
                dest.flush()
                state = {"status": "running", **counts}
                (out / "plan_summary.json").write_text(json.dumps(state, indent=2)+"\n")
                if counts["requested"] % 10000 == 0:
                    print(json.dumps(state), flush=True)
        state = {"status": "complete", **counts}
        (out / "plan_summary.json").write_text(json.dumps(state, indent=2)+"\n")
        print(json.dumps(state), flush=True)
    finally:
        for conn in connections:
            conn.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", required=True)
    parser.add_argument("--manifest")
    parser.add_argument("--output", required=True)
    parser.add_argument("--workers", type=int, default=4)
    parser.add_argument("--action", choices=("plan", "refine", "apply", "move", "verify"), default="plan")
    parser.add_argument("--source", default="good-places:2:20261021")
    parser.add_argument("--api", default="http://hopper-api:8081")
    parser.add_argument("--token", default="~/.tok/hopper")
    args = parser.parse_args()
    if args.workers < 1:
        parser.error("workers must be positive")
    if args.action == "plan":
        if not args.manifest:
            parser.error("plan requires --manifest")
        plan(args)
    elif args.action == "refine":
        refine(args)
    elif args.action == "apply":
        apply(args)
    elif args.action == "move":
        move(args)
    else:
        verify(args)


if __name__ == "__main__":
    main()
