"""Losslessly archive completed-run logs/states; retain the originals locally."""
import argparse
import gzip
import hashlib
import json
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]


def sha(data):
    return hashlib.sha256(data).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--results-dir", type=Path, default=BASE / "results")
    args = parser.parse_args()
    records = []
    paths = sorted([*args.results_dir.glob("*.log"), *args.results_dir.glob("*.state.json")])
    if not paths:
        raise ValueError("No raw logs or recovery states; existing archive manifest left unchanged")
    for path in paths:
        name = path.name.removesuffix(".log").removesuffix(".state.json")
        receipt = json.loads((args.results_dir / (name + ".run.json")).read_text())
        if receipt.get("returncode") != 0:
            raise ValueError(f"Do not archive an unfinished run: {name}")
        raw = path.read_bytes()
        destination = path.with_name(path.name + ".gz")
        if not destination.exists():
            with destination.open("xb") as output:
                output.write(gzip.compress(raw, mtime=0))
        compressed = destination.read_bytes()
        if gzip.decompress(compressed) != raw:
            raise ValueError(f"Archive roundtrip mismatch: {path}")
        records.append({"original": path.name, "sha256": sha(raw), "bytes": len(raw),
                        "archive": destination.name, "archive_sha256": sha(compressed),
                        "archive_bytes": len(compressed), "roundtrip_verified": True})
    (args.results_dir / "log-archives.json").write_text(json.dumps({"files": records}, indent=2) + "\n")
    print(f"Verified {len(records)} lossless archives; original files retained locally")


if __name__ == "__main__":
    main()
