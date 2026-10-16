#!/usr/bin/env python3
"""Read the community build contract; source config stays at version 'dev'."""
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]


def metadata(arch, release_tag="", prerelease=False):
    config = json.loads((ROOT / "traefik/config.json").read_text())
    bases = json.loads((ROOT / "traefik/build.json").read_text())["build_from"]
    if config["version"] != "dev" or set(config["arch"]) != set(bases):
        raise ValueError("Community source config must use version dev and matching base architectures")
    if arch not in bases:
        raise ValueError("Unsupported architecture")
    revision = os.environ.get("GITHUB_SHA") or subprocess.check_output(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    if not re.fullmatch(r"[a-f0-9]{40}", revision):
        raise ValueError("Invalid source revision")
    version = release_tag.removeprefix("v") if release_tag else revision[:7]
    if release_tag and not re.fullmatch(r"\d+\.\d+\.\d+(?:-[0-9A-Za-z.-]+)?", version):
        raise ValueError("Release tag must be a semantic version")
    if release_tag and "-" in version and not prerelease:
        raise ValueError("Prerelease tags must be published as prereleases")
    channel = ("beta" if prerelease else "stable") if release_tag else "edge"
    text = (ROOT / "traefik/Dockerfile").read_text()
    admin = re.search(r"^ARG TRAEFIK_ADMIN_VERSION=(\S+)$", text, re.M).group(1)
    return dict(base=bases[arch], image=config["image"].replace("{arch}", arch),
                manifest=config["image"].removesuffix("/{arch}"), version=version,
                channel=channel, admin_version=f"v{admin}", revision=revision,
                name=config["name"], description=config["description"],
                build_date=datetime.now(timezone.utc).isoformat(timespec="seconds"))


if __name__ == "__main__":
    values = metadata(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "",
                      os.environ.get("RELEASE_PRERELEASE", "false") == "true")
    for key, value in values.items():
        print(f"{key}={value}")
