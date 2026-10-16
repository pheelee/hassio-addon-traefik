import importlib.util
from pathlib import Path
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location("metadata", Path(__file__).resolve().parents[1] / "scripts/image-metadata.py")
metadata = importlib.util.module_from_spec(spec)
spec.loader.exec_module(metadata)


class MetadataTests(unittest.TestCase):
    def setUp(self):
        self.env = patch.dict("os.environ", {"GITHUB_SHA": "a" * 40})
        self.env.start()
        self.addCleanup(self.env.stop)

    def test_edge_uses_commit_version(self):
        result = metadata.metadata("amd64")
        self.assertEqual((result["channel"], result["version"]), ("edge", "aaaaaaa"))
        self.assertEqual(result["image"], "ghcr.io/pheelee/traefik/amd64")

    def test_release_channels(self):
        for tag, prerelease, channel, version in (
            ("v0.5.5", False, "stable", "0.5.5"),
            ("v0.5.5-rc.1", True, "beta", "0.5.5-rc.1"),
        ):
            with self.subTest(tag=tag):
                result = metadata.metadata("aarch64", tag, prerelease)
                self.assertEqual((result["channel"], result["version"]), (channel, version))

    def test_reject_unmarked_prerelease(self):
        with self.assertRaises(ValueError):
            metadata.metadata("amd64", "v0.5.5-rc.1")

    def test_reject_invalid_tag(self):
        with self.assertRaises(ValueError):
            metadata.metadata("amd64", "release/latest")

    def test_reject_retired_architecture(self):
        with self.assertRaises(ValueError):
            metadata.metadata("armv7")
