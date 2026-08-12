import tempfile
import unittest
from pathlib import Path
import sys
import types

sys.modules.setdefault("psutil", types.SimpleNamespace())
from app import file_hash, fmt_size


class UtilityTests(unittest.TestCase):
    def test_sizes(self):
        self.assertEqual(fmt_size(1024), "1.0 KB")
        self.assertEqual(fmt_size(1024 ** 3), "1.0 GB")

    def test_sha256(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample"
            path.write_bytes(b"nightowl")
            self.assertEqual(file_hash(path), "882099af2b09373f44dfc974cacee3830f1ab7fd8954e732f4f07ed15cf754d9")


if __name__ == "__main__":
    unittest.main()
