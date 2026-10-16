#!/usr/bin/env python3
"""Keep local builds, Home Assistant and CI on the same image configuration."""
import json
from pathlib import Path
import re
import sys

root = Path(__file__).resolve().parents[1]
config = json.loads((root / "config.json").read_text())
bases = json.loads((root / "build.json").read_text())["build_from"]
assert set(config["arch"]) == set(bases), "Base images must cover every supported architecture"
assert re.fullmatch(r"\d+\.\d+\.\d+", config["version"]), "Invalid add-on version"
arch = sys.argv[1]
release_tag = sys.argv[2] if len(sys.argv) > 2 else ""
assert not release_tag or release_tag in (config["version"], "v" + config["version"]), "Release tag must match config.json"
assert arch in config["arch"], "Unsupported architecture"
text = (root / "Dockerfile").read_text()
admin = re.search(r"^ARG TRAEFIK_ADMIN_VERSION=(\S+)$", text, re.M).group(1)
print(f"base={bases[arch]}")
print(f"image={config['image'].replace('{arch}', arch)}")
print(f"version={config['version']}")
print(f"admin_version=v{admin}")
