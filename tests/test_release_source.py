import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location("release_source", Path(__file__).resolve().parents[1] / "scripts/check-release-source.py")
source = importlib.util.module_from_spec(spec)
spec.loader.exec_module(source)
SHA = "a" * 40
MAIN = "b" * 40


class ReleaseSourceTests(unittest.TestCase):
    def validate(self, tag="v1.0.0", prerelease=False, status="ahead", revision=SHA, **changes):
        event = {"action": "published", "release": {"tag_name": tag, "prerelease": prerelease, "draft": False}}
        event["release"].update(changes)
        def fetch(path):
            if "/compare/" in path:
                self.assertTrue(path.endswith(f"{SHA}...{MAIN}"))
                return {"status": status}
            return {"sha": MAIN if path.endswith("/main") else revision}
        source.validate("release", event, source.REPOSITORY, f"refs/tags/{tag}", SHA, fetch)

    def test_reviewed_release_and_prerelease(self):
        self.validate()
        self.validate(status="identical")
        self.validate(tag="v1.0.0-rc.1", prerelease=True)

    def test_off_main_releases_rejected(self):
        for status in ("behind", "diverged"):
            with self.subTest(status=status), self.assertRaisesRegex(ValueError, "main history"):
                self.validate(status=status)

    def test_moved_tag_rejected(self):
        with self.assertRaisesRegex(ValueError, "no longer matches"):
            self.validate(revision=MAIN)

    def test_draft_invalid_tag_and_channel_mismatch_rejected(self):
        for changes in ({"draft": True}, {"tag": "../main"}, {"tag": "v1.0.0-rc.1"},
                        {"prerelease": True}, {"tag": "v01.0.0"},
                        {"tag": "v1.0.0-rc.01", "prerelease": True}):
            with self.subTest(changes=changes), self.assertRaises(ValueError):
                self.validate(**changes)

    def test_only_latest_main_push_can_publish_edge(self):
        fetch = lambda _: {"sha": MAIN}
        source.validate("push", {}, source.REPOSITORY, "refs/heads/main", MAIN, fetch)
        for ref, revision in (("refs/heads/main", SHA), ("refs/heads/other", MAIN)):
            with self.assertRaises(ValueError):
                source.validate("push", {}, source.REPOSITORY, ref, revision, fetch)

    def test_unexpected_repository_or_event_rejected(self):
        with self.assertRaises(ValueError):
            source.validate("push", {}, "other/repo", "refs/heads/main", MAIN)
        with self.assertRaises(ValueError):
            source.validate("workflow_dispatch", {}, source.REPOSITORY, "refs/heads/main", MAIN,
                            lambda _: {"sha": MAIN})

    def test_credentials_and_deployment_wait_for_source_validation(self):
        import yaml
        workflow = yaml.safe_load((Path(source.__file__).resolve().parents[1] / ".github/workflows/publish.yml").read_text())
        jobs = workflow["jobs"]
        self.assertEqual(jobs["catalog"]["needs"], "source")
        self.assertIn("source", jobs["deploy"]["needs"])
        self.assertEqual(jobs["source"]["permissions"], {"contents": "read"})
        self.assertEqual(jobs["source"]["steps"][0]["with"]["ref"], "main")
