"""Protect the published archive manifest when raw inputs are absent."""
import gzip
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


class ArchiveCustody(unittest.TestCase):
    def test_archive_only_checkout_preserves_retained_evidence(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            raw = b"Finished match\n"
            compressed = gzip.compress(raw, mtime=0)
            (root / "finished.log.gz").write_bytes(compressed)
            (root / "finished.run.json").write_text('{"returncode": 0}\n')
            record = {"original": "finished.log", "bytes": len(raw),
                      "sha256": hashlib.sha256(raw).hexdigest(),
                      "archive": "finished.log.gz", "archive_bytes": len(compressed),
                      "archive_sha256": hashlib.sha256(compressed).hexdigest(),
                      "roundtrip_verified": True}
            (root / "log-archives.json").write_text(json.dumps({"files": [record]}) + "\n")
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            script = Path(__file__).with_name("archive_logs.py")
            result = subprocess.run([sys.executable, str(script), "--results-dir", str(root)],
                                    capture_output=True, text=True)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual({p.name: p.read_bytes() for p in root.iterdir()}, before)


if __name__ == "__main__":
    unittest.main()
