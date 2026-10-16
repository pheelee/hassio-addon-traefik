#!/usr/bin/env python3
"""Fail closed before publishing commits outside the protected main history."""
import json
import os
from pathlib import Path
import re
import subprocess

REPOSITORY = "pheelee/hassio-addon-traefik"
TAG = re.compile(r"v?(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)(?:-[0-9a-z-]+(?:\.[0-9a-z-]+)*)?")


def api(path):
    return json.loads(subprocess.check_output(["gh", "api", path], text=True))


def validate(event_name, event, repository, ref, revision, fetch=api):
    if repository != REPOSITORY or not re.fullmatch(r"[a-f0-9]{40}", revision):
        raise ValueError("Unexpected repository or revision")
    main = fetch(f"repos/{REPOSITORY}/commits/main")["sha"]
    if event_name == "push":
        if ref != "refs/heads/main" or revision != main:
            raise ValueError("Only the current main commit may publish edge images")
    elif event_name == "release":
        release = event["release"]
        tag = release["tag_name"]
        if event.get("action") != "published" or release["draft"] or not TAG.fullmatch(tag):
            raise ValueError("Expected a published semantic version tag")
        if any(part.isdigit() and len(part) > 1 and part.startswith("0")
               for part in tag.partition("-")[2].split(".")):
            raise ValueError("Numeric prerelease identifiers cannot have leading zeroes")
        if bool("-" in tag) != release["prerelease"] or ref != f"refs/tags/{tag}":
            raise ValueError("Release channel or ref does not match its tag")
        if fetch(f"repos/{REPOSITORY}/commits/{tag}")["sha"] != revision:
            raise ValueError("Release tag no longer matches the triggering commit")
        comparison = fetch(f"repos/{REPOSITORY}/compare/{revision}...{main}")
        if comparison["status"] not in ("ahead", "identical"):
            raise ValueError("Release commit must belong to reviewed main history")
    else:
        raise ValueError("Unexpected publishing event")


if __name__ == "__main__":
    validate(os.environ["GITHUB_EVENT_NAME"],
             json.loads(Path(os.environ["GITHUB_EVENT_PATH"]).read_text()),
             os.environ["GITHUB_REPOSITORY"], os.environ["GITHUB_REF"], os.environ["GITHUB_SHA"])
    print("PASS: publishing source belongs to protected main history")
