#!/usr/bin/env python3
"""Copy error-report samples into a clean triage directory.

Samples are fetched from hopper's ``GET /api/file/{sha256}`` endpoint by
sha256. Local-disk lookup was removed: sample paths come from the hopper
DB and may be absolute paths from whatever host ingested them (e.g.
``/Users/t/...``), which don't exist on the triage host. Defaults to
``HOPPER_URL`` from the env, or http://hopper-api:8081/.

Archive members are fetched as their WHOLE containing archive (the row's
``parent`` sha) rather than asking hopper to stream-extract each member —
a stored-blob read is ~0.2s where an in-archive extract can run for
minutes, and one archive covers all of its flagged members. Each sha is
downloaded at most once per run; a repeat (sibling member, the same
archive under another filetype, or a file already on disk) is reused.
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

DEFAULT_HOPPER_URL = "http://hopper-api:8081"


def _hopper_token() -> str:
    """The bearer token for hopper API calls, or "" if there is none.

    Same precedence as every other client in the fleet (hopper/token.go,
    scan's worker): $HOPPER_TOKEN wins, otherwise the first non-empty line of
    ~/.tok/hopper — the file the deploy scripts install. The line, not the
    file: editors and shell redirects leave a trailing newline. An empty
    result is correct against an unauthenticated master and earns an honest
    401 against an authenticated one.
    """
    env = os.environ.get("HOPPER_TOKEN", "").strip()
    if env:
        return env
    try:
        with open(Path.home() / ".tok" / "hopper", encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    return line.strip()
    except OSError:
        pass
    return ""


def _parse_retry_after(value: str | None) -> float | None:
    """Parse a Retry-After header (hopper sends delta-seconds) into a float.

    Returns None if absent or unparseable (e.g. an HTTP-date form), so the
    caller falls back to its own retry schedule.
    """
    if not value:
        return None
    try:
        return max(0.0, float(value.strip()))
    except ValueError:
        return None


def _fetch_from_hopper(
    sha256: str,
    destination: Path,
    hopper_url: str,
    timeout: float = 45.0,
    retry_delays: tuple[float, ...] = (3.0, 12.0),
) -> tuple[str, str]:
    """GET /api/file/{sha256} → destination.

    Returns ``(status, detail)`` where ``detail`` is a short human-readable
    reason (the server response for HTTP errors, the exception for network
    failures) and ``status`` is one of:
      "ok"          file written to ``destination``.
      "unservable"  hopper gave a DEFINITIVE code for this sha — 400 (bad sha),
                    404 (not in DB/archive), 410 (row exists, file deleted from
                    disk), 413 (member too large), 415 (unsupported container),
                    422 (encrypted/corrupt/extraction-failed). It's up but won't
                    ever serve this sha, so the caller can fall back to fetching
                    the parent archive whole. Does NOT count toward the breaker.
      "unreachable" no usable response after all retries — either a network
                    failure (timeout/refused/DNS) or a RETRYABLE server error
                    (500 DB-lookup error, 503 starting/busy/transient-I/O) that
                    never cleared. This is what the dead-service breaker counts.

    The split is retryable-vs-definitive, not code-vs-no-response: hopper signals
    transient trouble with 500/503 (and a 503 carries a Retry-After telling us
    how long to wait), so those join the network-failure retry path. A 4xx/410/
    422 is hopper's final answer for this sha, so it isn't retried.

    Network failures and 500s back off on the ``retry_delays`` schedule (3s then
    12s by default); a 503 waits its Retry-After instead. Each sleep gets up to
    +25% additive jitter so concurrent fetches don't resynchronize.
    """
    if not sha256:
        return "unservable", "no sha256 in row"
    url = f"{hopper_url.rstrip('/')}/api/file/{sha256}"
    request = urllib.request.Request(url)
    token = _hopper_token()
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    detail = "unknown"
    retries = len(retry_delays)
    for attempt in range(retries + 1):
        retry_after = None  # set only by a 503 → overrides the schedule
        try:
            destination.parent.mkdir(parents=True, exist_ok=True)
            with urllib.request.urlopen(request, timeout=timeout) as resp:
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
            detail = f"HTTP {e.code} {body}".strip()
            # 500 (DB-lookup hiccup) and 503 (starting/busy/transient I/O) are
            # hopper telling us to try again; a 503 also carries a Retry-After.
            # Every other code is its final answer for this sha — don't retry;
            # the caller may fall back to the parent archive.
            if e.code not in (500, 503):
                return "unservable", detail
            if e.code == 503:
                retry_after = _parse_retry_after(e.headers.get("Retry-After"))
        except (urllib.error.URLError, OSError, TimeoutError) as e:
            # No HTTP response at all — refused, DNS failure, or timeout.
            reason = getattr(e, "reason", None) or e
            detail = f"{type(e).__name__}: {reason}"
        if attempt < retries:
            base = retry_after if retry_after is not None else retry_delays[attempt]
            delay = base + random.uniform(0.0, 0.25 * base)
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
    landed: dict[str, Path],
    copied: list[str],
    fetched: list[str],
    missing: list[str],
    errors: list[dict[str, Any]] | None = None,
    hopper_failures: list[int] | None = None,
    hopper_failure_limit: int = 10,
    fetch_delay: float = 0.0,
) -> tuple[int, Counter]:
    """Fetch up to ``top`` obtainable samples from hopper into ``base_dir``.

    Archive members are served as their WHOLE containing archive (the row's
    ``parent`` sha) rather than asking hopper to stream-extract the member: a
    stored-blob read is ~0.2s where an in-archive extract can run for minutes,
    and one archive download covers every flagged member inside it. The
    reviewer opens the landed archive to inspect the member that flagged.

    Each sha is downloaded at most once per run (tracked in ``landed``): a
    repeat — a sibling member, the same archive flagged under another filetype,
    or a file already on disk — is reused without hitting the network. Keeps
    scanning past rows hopper can't serve until ``top`` files actually land.
    Mutates the shared accumulators. Returns ``(landed_count, skip_reasons)``
    where ``skip_reasons`` tallies, by server response, why rows didn't land.
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
        _, outer_arcname = resolved

        raw_path = str(row.get("path") or "")
        is_archive_member = "!!" in raw_path
        target_sha = str(row.get("sha256") or "")
        parent_sha = str(row.get("parent") or "")

        # Archive member → grab the whole containing archive (its `parent` sha)
        # as a stored blob; the reviewer inspects the flagged member inside it.
        # Standalone files, and the rare member with no recorded parent, fetch
        # by their own sha.
        if is_archive_member and parent_sha and parent_sha != target_sha:
            fetch_sha = parent_sha
        else:
            fetch_sha = target_sha
        if not fetch_sha:
            missing.append(raw_path)
            skipped["no sha256 in row"] += 1
            _record_error(row, raw_path, "unservable", "no sha256 in row")
            continue

        # Sha-stamp the landed name so same-named archives of differing content
        # can't collide — keeps the on-disk reuse check below sound.
        destination = base_dir / f"{fetch_sha[:12]}__{outer_arcname}"

        # Already have these bytes? Reuse them instead of re-downloading.
        prior = landed.get(fetch_sha)
        if prior is not None and prior.exists():
            if prior == destination:
                # A sibling member of an archive already landed in this bucket —
                # don't spend a quota slot on a file that's already here.
                continue
            # Same archive needed under another filetype: copy it across locally
            # rather than fetching it again, and count it toward this bucket.
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(prior, destination)
            copied.append(str(destination.relative_to(base_dir)))
            here += 1
            continue
        if destination.exists():
            # Left on disk by a prior run (or pre-placed) — reuse as-is.
            landed[fetch_sha] = destination
            copied.append(str(destination.relative_to(base_dir)))
            here += 1
            continue

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

        # Throttle: hopper is single-streamed and falls behind under rapid-fire
        # requests. A small gap between requests keeps it responsive.
        if fetch_delay > 0:
            time.sleep(fetch_delay)
        # Whole archives can be large, so allow a generous transfer window — it's
        # still a stored-blob read, not extraction. Standalone files respond fast.
        timeout = 180.0 if is_archive_member else 45.0
        status, detail = _fetch_from_hopper(fetch_sha, destination, hopper_url, timeout=timeout)
        if status == "ok":
            if hopper_failures is not None:
                hopper_failures[0] = 0
            landed[fetch_sha] = destination
            print(f"  hopper: fetched {fetch_sha[:12]}… → {destination.name}", flush=True)
            fetched.append(str(destination.relative_to(base_dir)))
            copied.append(str(destination.relative_to(base_dir)))
            here += 1
            continue

        if status == "unreachable":
            if hopper_failures is not None:
                hopper_failures[0] += 1
            # A genuine no-response failure (hopper down) — rare and worth
            # surfacing individually with the reason.
            print(f"  hopper: FAILED {fetch_sha[:12]}… {detail}", flush=True)

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

    landed: dict[str, Path] = {}  # sha256 -> first on-disk path, deduped run-wide
    copied: list[str] = []
    missing: list[str] = []
    fetched: list[str] = []
    errors: list[dict[str, Any]] = []
    hopper_failures: list[int] = [0]

    rows = _rows(payload, kind)
    if skip > 0:
        rows = rows[skip:]

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
                landed=landed,
                copied=copied,
                fetched=fetched,
                missing=missing,
                errors=errors,
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
            landed=landed,
            copied=copied,
            fetched=fetched,
            missing=missing,
            errors=errors,
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
        default=float(os.environ.get("TRIAGE_FETCH_DELAY", "0.0")),
        help="Seconds to pause before each hopper fetch, to keep the single-"
             "streamed download API responsive under load (default 0, or "
             "$TRIAGE_FETCH_DELAY). Raise it if hopper flaps under back-to-back "
             "requests.",
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
