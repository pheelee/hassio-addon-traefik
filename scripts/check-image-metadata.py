#!/usr/bin/env python3
"""Reject inherited base metadata on the packaged add-on image."""
import json
import os
import subprocess
import sys

image, architecture, version = sys.argv[1:]
info = json.loads(subprocess.check_output(["docker", "image", "inspect", image], text=True))[0]
labels = info["Config"]["Labels"]
if info["Architecture"] != {"amd64": "amd64", "aarch64": "arm64"}[architecture]:
    raise SystemExit("Image architecture does not match its add-on architecture label")
expected = {
    "io.hass.type": "addon",
    "io.hass.arch": architecture,
    "io.hass.version": version,
    "org.opencontainers.image.version": version,
    "org.opencontainers.image.source": "https://github.com/pheelee/hassio-addon-traefik",
    "org.opencontainers.image.licenses": "MIT",
}
if revision := os.environ.get("GITHUB_SHA"):
    expected["org.opencontainers.image.revision"] = revision
for key, value in expected.items():
    if labels.get(key) != value:
        raise SystemExit(f"Incorrect image metadata: {key}={labels.get(key)!r}; expected {value!r}")
print("PASS: add-on and OCI image metadata")
