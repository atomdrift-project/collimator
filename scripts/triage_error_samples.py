#!/usr/bin/env python3
"""Copy error-report samples into a clean triage directory.

Samples are fetched from hopper's ``GET /api/file/{sha256}`` endpoint by
sha256. Local-disk lookup was removed: sample paths come from the hopper
DB and may be absolute paths from whatever host ingested them (e.g.
``/Users/t/...``), which don't exist on the triage host. Defaults to
``HOPPER_URL`` from the env, or http://10.9.8.5:8081/.
"""

from __future__ import annotations

import argparse
import json
import os
import random
import shutil
import tempfile
import time
import urllib.error
import urllib.request
from collections import Counter
from pathlib import Path
from typing import Any

from archive_error_samples import _rows, _sample_path

DEFAULT_HOPPER_URL = "http://10.9.8.5:8081"


def _fetch_from_hopper(
    sha256: str,
    destination: Path,
    hopper_url: str,
    timeout: float = 10.0,
    retries: int = 2,
    backoff: float = 0.5,
    backoff_cap: float = 8.0,
) -> tuple[str, str]:
    """GET /api/file/{sha256} → destination.

    Returns ``(status, detail)`` where ``detail`` is a short human-readable
    reason (the server response for HTTP errors, the exception for network
    failures) and ``status`` is one of:
      "ok"          file written to ``destination``.
      "unservable"  hopper ANSWERED with an error code (any 4xx or 5xx). It's
                    alive but won't serve this sha — typically an archive member
                    it can't extract: 415 "unsupported archive type", 413 "file
                    too large", 404 "not found in archive", 500 "extraction
                    failed". The caller can fall back to fetching the parent
                    archive whole. Does NOT count toward the dead-service breaker.
      "unreachable" NO response after ``retries`` — timeout or refused
                    connection. This is what the dead-service breaker counts.

    The received-code-vs-no-response split is the signal: if hopper replied at
    all it's up (try the parent), only a silent connection counts as down.

    No-response failures are retried with exponential backoff and full jitter
    (sleep ∈ [0, min(cap, backoff·2^attempt))): under a burst hopper occasionally
    can't answer in time, and a lone blip shouldn't read as a dead service. An
    error *code* is hopper's definitive answer for that sha, so it isn't retried.
    """
    if not sha256:
        return "unservable", "no sha256 in row"
    url = f"{hopper_url.rstrip('/')}/api/file/{sha256}"
    detail = "unknown"
    for attempt in range(retries + 1):
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(url, timeout=timeout) as resp:
                if resp.status != 200:
                    body = resp.read(200).decode("utf-8", "replace").strip()
                    return "unservable", f"HTTP {resp.status} {body}".strip()
                tmp = destination.with_suffix(destination.suffix + ".tmp")
                with open(tmp, "wb") as f:
                    shutil.copyfileobj(resp, f)
                tmp.rename(destination)
            return "ok", ""
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read(200).decode("utf-8", "replace").strip()
            except Exception:
                pass
            # Hopper answered — it's up, this sha just isn't servable. Definitive
            # for this request (no retry); the caller may try the parent archive.
            return "unservable", f"HTTP {e.code} {body}".strip()
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            # No HTTP response at all — refused, DNS failure, or timeout.
            reason = getattr(e, "reason", None) or e
            detail = f"{type(e).__name__}: {reason}"
        if attempt < retries:
            delay = random.uniform(0.0, min(backoff_cap, backoff * (2 ** attempt)))
            print(
                f"  hopper: {sha256[:12]}… {detail} — retry "
                f"{attempt + 1}/{retries} in {delay:.2f}s",
                flush=True,
            )
            time.sleep(delay)
    return "unreachable", detail



_TEMP_ROOTS = (Path("/var/tmp"), Path(tempfile.gettempdir()))


def _clear_directory(path: Path) -> None:
    resolved = path.resolve(strict=False)
    inside_temp = False
    for root in _TEMP_ROOTS:
        r = root.resolve(strict=False)
        try:
            if os.path.commonpath([str(resolved), str(r)]) == str(r) and resolved != r:
                inside_temp = True
                break
        except ValueError:
            pass
    if not inside_temp:
        raise ValueError(f"refusing to clear non-temp triage directory: {path}")
    path.mkdir(parents=True, exist_ok=True)
    for child in path.iterdir():
        if child.is_dir() and not child.is_symlink():
            shutil.rmtree(child)
        else:
            child.unlink()


def _copy_rows(
    rows: list[dict[str, Any]],
    *,
    base_dir: Path,
    samples_dir: Path,
    top: int,
    hopper_url: str | None,
    seen: set[Path],
    copied: list[str],
    fetched: list[str],
    missing: list[str],
    errors: list[dict[str, Any]] | None = None,
    archives: dict[str, str] | None = None,
    extract_members: bool = True,
    hopper_failures: list[int] | None = None,
    hopper_failure_limit: int = 10,
    fetch_delay: float = 0.0,
) -> tuple[int, Counter]:
    """Fetch up to ``top`` obtainable samples from hopper into ``base_dir``.

    Keeps scanning past rows hopper can't serve until ``top`` files actually
    land — so feeding a larger candidate pool than ``top`` covers samples
    absent from hopper. Mutates the shared accumulators. Returns
    ``(landed, skip_reasons)`` where ``skip_reasons`` tallies, by server
    response, why rows didn't land (so the caller can surface the breakdown).

    When ``extract_members`` is False, archive members land under the outer
    archive's name (deduped across members) rather than in a per-member subdir.
    """
    here = 0
    skipped: Counter[str] = Counter()

    def _record_error(row: dict[str, Any], path: str, status: str, detail: str) -> None:
        if errors is not None:
            errors.append({
                "row_id": row.get("row_id"),
                "filetype": row.get("filetype"),
                "sha256": row.get("sha256") or "",
                "path": path,
                "status": status,
                "detail": detail,
            })

    for row in rows:
        if here >= top:
            break
        resolved = _sample_path(samples_dir, row)
        if resolved is None:
            continue
        outer_path, outer_arcname = resolved

        raw_path = str(row.get("path") or "")
        is_archive_member = "!!" in raw_path
        member_name = raw_path.split("!!", 1)[1] if is_archive_member else None

        # For member extraction: dedupe on (outer_path, member_name).
        # When copying whole archives: dedupe on outer_path so multiple members
        # of the same archive only copy it once.
        if is_archive_member and extract_members:
            dedupe_key = outer_path.resolve(strict=False) / (member_name or "")
        else:
            dedupe_key = outer_path.resolve(strict=False)
        if dedupe_key in seen:
            continue
        seen.add(dedupe_key)

        if is_archive_member and extract_members:
            # Place the extracted member under <outer_arcname>/<member_name>
            # so the archive it came from is visible in the path.
            destination = base_dir / outer_arcname / member_name
        else:
            destination = base_dir / outer_arcname

        # Fetch from hopper by sha256 — the only source.
        if not hopper_url:
            missing.append(raw_path)
            skipped["hopper fetch disabled"] += 1
            _record_error(row, raw_path, "skipped", "hopper fetch disabled")
            continue

        # Skip hopper if it has failed too many consecutive times (dead service).
        if hopper_failures is not None and hopper_failures[0] >= hopper_failure_limit:
            if hopper_failures[0] == hopper_failure_limit:
                print(f"  hopper: {hopper_failure_limit} consecutive failures — skipping remaining hopper fetches", flush=True)
                hopper_failures[0] += 1  # only print once
            missing.append(raw_path)
            skipped["skipped after breaker tripped"] += 1
            _record_error(row, raw_path, "skipped", "breaker tripped")
            continue

        # Hopper serves standalone files and members of the archive types it
        # can extract (gz/jar/vsix/…) directly by the row's sha256.
        target_sha = str(row.get("sha256") or "")
        parent_sha = str(row.get("parent") or "")
        # Throttle: hopper is single-streamed and falls behind under rapid-fire
        # requests (members trigger extraction work), timing out and tripping
        # the breaker. A small gap between requests keeps it responsive.
        if fetch_delay > 0:
            time.sleep(fetch_delay)
        if target_sha:
            status, detail = _fetch_from_hopper(target_sha, destination, hopper_url)
        else:
            status, detail = "unservable", "no sha256 in row"
        if status == "ok":
            if hopper_failures is not None:
                hopper_failures[0] = 0
            print(f"  hopper: fetched {target_sha[:12]}… → {destination.name}", flush=True)
            fetched.append(str(destination.relative_to(base_dir)))
            copied.append(str(destination.relative_to(base_dir)))
            here += 1
            continue

        # Couldn't serve the member directly. Fall back to the containing
        # archive (its `parent` sha): hopper serves the whole archive as a
        # stored blob even when it can't extract the member — e.g. an embedded
        # file in a PE, or a member of a nested/unsupported archive type. Many
        # members map to one parent, so dedupe the archive fetch via `archives`.
        if is_archive_member and parent_sha and parent_sha != target_sha:
            cached = archives.get(parent_sha) if archives is not None else None
            if cached == "ok":
                continue  # archive already fetched for a sibling member
            if cached is None:
                archive_dest = base_dir / "_archives" / outer_arcname
                if fetch_delay > 0:
                    time.sleep(fetch_delay)
                pstatus, pdetail = _fetch_from_hopper(parent_sha, archive_dest, hopper_url)
                if archives is not None:
                    archives[parent_sha] = "ok" if pstatus == "ok" else f"{pstatus}: {pdetail}"
                if pstatus == "ok":
                    if hopper_failures is not None:
                        hopper_failures[0] = 0
                    print(f"  hopper: member unservable → fetched parent archive "
                          f"{parent_sha[:12]}… → {archive_dest.name}", flush=True)
                    fetched.append(str(archive_dest.relative_to(base_dir)))
                    copied.append(str(archive_dest.relative_to(base_dir)))
                    here += 1
                    continue
                status, detail = pstatus, f"member {detail} → parent {pdetail}"
            else:
                status = "unreachable" if cached.startswith("unreachable") else "unservable"
                detail = f"member {detail} → parent {cached}"

        if status == "unreachable":
            if hopper_failures is not None:
                hopper_failures[0] += 1
            # A genuine no-response failure (hopper down) — rare and worth
            # surfacing individually with the reason.
            print(f"  hopper: FAILED {target_sha[:12]}… {detail}", flush=True)

        missing.append(raw_path)
        skipped[detail] += 1
        _record_error(row, raw_path, status, detail)
    return here, skipped


def copy_report(
    *,
    report_path: Path,
    output_dir: Path,
    samples_dir: Path,
    kind: str,
    top: int,
    hopper_url: str | None = None,
    skip: int = 0,
    group_by_filetype: bool = False,
    fetch_delay: float = 0.0,
    error_report: Path | None = None,
) -> dict[str, Any]:
    with open(report_path) as f:
        payload = json.load(f)

    _clear_directory(output_dir)

    seen: set[Path] = set()
    copied: list[str] = []
    missing: list[str] = []
    fetched: list[str] = []
    errors: list[dict[str, Any]] = []
    archives: dict[str, str] = {}  # parent sha -> fetch outcome, deduped run-wide
    hopper_failures: list[int] = [0]

    rows = _rows(payload, kind)
    if skip > 0:
        rows = rows[skip:]

    extract_members = kind != "false-negatives"

    per_filetype: dict[str, int] = {}
    if group_by_filetype:
        # ``top`` is a PER-FILETYPE quota; each filetype lands in its own
        # subdir so the sorter can sweep one type at a time.
        groups: dict[str, list[dict[str, Any]]] = {}
        for row in rows:
            ft = str(row.get("filetype") or "unknown")
            groups.setdefault(ft, []).append(row)
        n_ft = len(groups)
        for i, (ft, ft_rows) in enumerate(sorted(groups.items()), 1):
            # Fresh breaker per filetype: hopper flaps (brief outages during a
            # rebuild) shouldn't abandon every remaining filetype. A flap now
            # costs at most this filetype's tail; the next one starts clean. A
            # truly-dead hopper still fails fast — connection-refused is instant.
            n, skipped = _copy_rows(
                ft_rows,
                base_dir=output_dir / ft,
                samples_dir=samples_dir,
                top=top,
                hopper_url=hopper_url,
                seen=seen,
                copied=copied,
                fetched=fetched,
                missing=missing,
                errors=errors,
                archives=archives,
                extract_members=extract_members,
                hopper_failures=[0],
                fetch_delay=fetch_delay,
            )
            per_filetype[ft] = n
            summary = f"  [{i}/{n_ft}] {ft}: {n} copied"
            if skipped:
                reasons = ", ".join(f"{c}× {r}" for r, c in skipped.most_common(4))
                summary += f" ({sum(skipped.values())} skipped: {reasons})"
            print(summary, flush=True)
    else:
        _, skipped = _copy_rows(
            rows,
            base_dir=output_dir,
            samples_dir=samples_dir,
            top=top,
            hopper_url=hopper_url,
            seen=seen,
            copied=copied,
            fetched=fetched,
            missing=missing,
            errors=errors,
            archives=archives,
            extract_members=extract_members,
            hopper_failures=hopper_failures,
            fetch_delay=fetch_delay,
        )
        if skipped:
            reasons = ", ".join(f"{c}× {r}" for r, c in skipped.most_common(6))
            print(f"  {sum(skipped.values())} skipped: {reasons}", flush=True)

    if error_report is not None:
        error_report.parent.mkdir(parents=True, exist_ok=True)
        with open(error_report, "w") as f:
            for rec in errors:
                f.write(json.dumps(rec) + "\n")
        print(f"  wrote {len(errors)} error records to {error_report}", flush=True)

    return {
        "report": str(report_path),
        "output_dir": str(output_dir),
        "samples_dir": str(samples_dir),
        "hopper_url": hopper_url or "",
        "kind": kind,
        "requested": top,
        "grouped_by_filetype": group_by_filetype,
        "filetypes": len(per_filetype),
        "per_filetype_copied": per_filetype,
        "copied": len(copied),
        "fetched_from_hopper": len(fetched),
        "parent_archives_fetched": sum(1 for v in archives.values() if v == "ok"),
        "errors_logged": len(errors),
        "missing": missing,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--samples-dir", default="/data/samples", type=Path)
    parser.add_argument(
        "--kind",
        choices=[
            "false-positives",
            "false-negatives",
            "near-false-positives",
            "near-false-negatives",
        ],
        required=True,
    )
    parser.add_argument("--top", type=int, default=100)
    parser.add_argument(
        "--group-by-filetype",
        action="store_true",
        help="Write each sample under <output-dir>/<filetype>/ and treat "
             "--top as a PER-FILETYPE quota (copy until --top land for each "
             "filetype). Pair with a report built via "
             "mislabeled_by_scope.py --per-filetype-top.",
    )
    parser.add_argument(
        "--skip",
        type=int,
        default=0,
        help="Skip the first N rows in the report before taking --top.",
    )
    parser.add_argument(
        "--hopper-url",
        default=os.environ.get("HOPPER_URL", DEFAULT_HOPPER_URL),
        help=(
            "Hopper download API base URL. Set to empty to disable the fallback "
            "fetch; default uses HOPPER_URL env or " + DEFAULT_HOPPER_URL
        ),
    )
    parser.add_argument(
        "--fetch-delay",
        type=float,
        default=float(os.environ.get("TRIAGE_FETCH_DELAY", "0.05")),
        help="Seconds to pause before each hopper fetch, to keep the single-"
             "streamed download API responsive under load (default 0.05, or "
             "$TRIAGE_FETCH_DELAY). Set 0 to fetch as fast as possible.",
    )
    parser.add_argument(
        "--error-report",
        type=Path,
        default=None,
        help="Write a JSONL record (row_id, filetype, sha256, path, status, "
             "detail) for every row that didn't land — for joining against the "
             "DB (size_bytes, file_type) to break errors down by filetype/size.",
    )
    args = parser.parse_args()

    summary = copy_report(
        report_path=args.report,
        output_dir=args.output_dir,
        samples_dir=args.samples_dir,
        kind=args.kind,
        top=args.top,
        hopper_url=args.hopper_url or None,
        skip=args.skip,
        group_by_filetype=args.group_by_filetype,
        fetch_delay=args.fetch_delay,
        error_report=args.error_report,
    )
    if summary["grouped_by_filetype"]:
        print(
            f"Copied {summary['copied']} unique {args.kind} samples across "
            f"{summary['filetypes']} filetype(s) "
            f"(target {summary['requested']}/filetype) to {summary['output_dir']}"
        )
    else:
        print(
            f"Copied {summary['copied']}/{summary['requested']} unique {args.kind} "
            f"samples to {summary['output_dir']}"
        )
    if summary["fetched_from_hopper"]:
        print(f"  ({summary['fetched_from_hopper']} fetched from hopper "
              f"at {summary['hopper_url']})")
    if summary["missing"]:
        print(f"Missing {len(summary['missing'])} paths (not on disk, not in hopper); first 10:")
        for path in summary["missing"][:10]:
            print(f"  {path}")


if __name__ == "__main__":
    main()
