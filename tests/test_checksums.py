import hashlib
from pathlib import Path
import subprocess
import tempfile
import unittest

VERIFY = Path(__file__).resolve().parents[1] / "traefik/scripts/verify-sha256.sh"


class ChecksumTests(unittest.TestCase):
    def verify(self, manifest, data=b"release asset"):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder)
            (path / "asset.tar.gz").write_bytes(data)
            (path / "SHA256SUMS").write_text(manifest)
            return subprocess.run(
                ["sh", str(VERIFY), "SHA256SUMS", "asset.tar.gz"],
                cwd=path, capture_output=True,
            ).returncode

    def setUp(self):
        self.digest = hashlib.sha256(b"release asset").hexdigest()
        self.entry = f"{self.digest}  asset.tar.gz\n"

    def test_exact_asset_with_unrelated_entries(self):
        self.assertEqual(self.verify("0" * 64 + "  other.tar.gz\n" + self.entry), 0)

    def test_binary_marker(self):
        self.assertEqual(self.verify(f"{self.digest} *asset.tar.gz\n"), 0)

    def test_corrupted_asset(self):
        self.assertNotEqual(self.verify(self.entry, b"corrupted"), 0)

    def test_missing_asset(self):
        self.assertNotEqual(self.verify(f"{self.digest}  prefix-asset.tar.gz\n"), 0)

    def test_duplicate_asset(self):
        self.assertNotEqual(self.verify(self.entry * 2), 0)

    def test_malformed_digest(self):
        for digest in ("f" * 63, "z" * 64, "f" * 65):
            with self.subTest(digest=digest):
                self.assertNotEqual(self.verify(f"{digest}  asset.tar.gz\n"), 0)

    def test_extra_field(self):
        self.assertNotEqual(self.verify(self.entry.rstrip() + " extra\n"), 0)


if __name__ == "__main__":
    unittest.main()
