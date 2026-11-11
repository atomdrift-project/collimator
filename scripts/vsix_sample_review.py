#!/usr/bin/env python3
"""Read a fixed training-only sample list and inspect bytes with cleave facts."""
from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path, PurePosixPath
import subprocess
import urllib.request
import zipfile


def write(path, value):
    path.write_text(json.dumps(value, indent=2) + "\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("out/experiments/vsix-recall-20261104"))
    parser.add_argument("--url", default="http://hopper-api:8081")
    parser.add_argument("--metadata", type=Path)
    args = parser.parse_args()
    metadata = args.metadata or args.root / "sample-review-metadata.jsonl"
    records = [json.loads(line) for line in metadata.read_text().splitlines()]
    selected = {r["id"]: r for r in json.loads((args.root / "sample-review-selection.json").read_text())}
    for record in records:
        selection = selected.get(record["id"], {"role": record.get("role", "local-comparison")})
        dest = args.root / "sample-review" / str(record["id"])
        dest.mkdir(parents=True, exist_ok=True)
        archive = Path(record["local_path"]) if record.get("local_path") else dest / "archive.vsix"
        if not archive.exists():
            token = (Path.home() / ".tok/hopper").read_text().strip()
            request = urllib.request.Request(args.url.rstrip("/") + "/api/file/" + record["sha256"],
                headers={"Authorization": "Bearer " + token})
            with urllib.request.urlopen(request, timeout=180) as response, archive.open("wb") as output:
                while block := response.read(1024 * 1024):
                    output.write(block)
        if hashlib.sha256(archive.read_bytes()).hexdigest() != record["sha256"]:
            raise ValueError("Downloaded bytes do not match the corpus hash")
        with zipfile.ZipFile(archive) as z:
            infos = z.infolist()
            names = {i.filename for i in infos}
            manifest_path = "extension/package.json" if "extension/package.json" in names else "package.json"
            manifest = json.loads(z.read(manifest_path))
            main_name = str(manifest.get("main") or manifest.get("browser") or "")
            if not main_name:
                candidates = [i for i in infos if i.filename.endswith((".js", ".cjs", ".mjs")) and "/node_modules/" not in i.filename]
                entry = max(candidates, key=lambda i: i.file_size).filename if candidates else None
            else:
                main_name = main_name.removeprefix("./")
                prefix = str(PurePosixPath(manifest_path).parent)
                candidates = [str(PurePosixPath(prefix) / main_name)]
                candidates += [candidates[0] + ".js", candidates[0] + "/index.js"]
                entry = next((name for name in candidates if name in names), None)
            if entry:
                (dest / "entrypoint.js").write_bytes(z.read(entry))
            info = {**record, **selection, "entrypoint_member": entry,
                "manifest": {k: manifest.get(k) for k in ("name", "publisher", "version", "main", "browser", "activationEvents", "extensionKind", "capabilities", "scripts", "dependencies")},
                "archive": {"members": len(infos), "expanded_bytes": sum(i.file_size for i in infos),
                            "compressed_bytes": sum(i.compress_size for i in infos),
                            "extensions": dict(Counter(PurePosixPath(i.filename).suffix.lower() for i in infos))}}
            write(dest / "summary.json", info)
        for name, path in (("archive", archive), ("entrypoint", dest / "entrypoint.js")):
            output = dest / (name + "-facts.json")
            if path.exists() and not output.exists():
                with output.open("w") as stream, (dest / (name + "-facts.stderr")).open("w") as errors:
                    result = subprocess.run(["cleave", "facts", "--json", str(path)], stdout=stream, stderr=errors, timeout=180)
                if result.returncode:
                    raise RuntimeError(f"cleave facts failed for {record['id']} {name}")
        print(record["id"], selection["role"], manifest.get("name"), entry, flush=True)


if __name__ == "__main__":
    main()
