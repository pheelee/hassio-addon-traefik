#!/usr/bin/env python3
"""Boot the packaged add-on and exercise a real Traefik route without ACME/SSO."""
import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import secrets
import subprocess
import tempfile
import time
from threading import Thread
import urllib.error
import urllib.request

CLIENT = urllib.request.build_opener(urllib.request.ProxyHandler({}))


def docker(*args):
    return subprocess.check_output(["docker", *args], text=True).strip()


def request(base, path, method="GET", data=None, host=None):
    headers = {"Content-Type": "application/json", "X-Requested-With": "XMLHttpRequest"}
    if host:
        headers["Host"] = host
    req = urllib.request.Request(base + path, data=None if data is None else json.dumps(data).encode(),
                                 headers=headers, method=method)
    try:
        with CLIENT.open(req, timeout=5) as response:
            return response.status, response.read()
    except urllib.error.HTTPError as error:
        return error.code, error.read()


def eventually(check, description):
    deadline = time.monotonic() + 90
    last = None
    while time.monotonic() < deadline:
        try:
            if check():
                return
        except (OSError, ValueError, KeyError) as error:
            last = error
        time.sleep(0.5)
    raise AssertionError(f"Timed out waiting for {description}: {last}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("image")
    parser.add_argument("--expected-version", required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    options = json.loads((root / "traefik/config.json").read_text())["options"]
    options.update(email="smoke@example.invalid", cookieSecret=secrets.token_hex(32))
    class SupervisorOptions(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path != "/addons/self/options/config":
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps({"result": "ok", "data": options}).encode())

        def log_message(self, *_args):
            pass

    supervisor = ThreadingHTTPServer(("0.0.0.0", 0), SupervisorOptions)
    Thread(target=supervisor.serve_forever, daemon=True).start()
    # The fixture serves only generated test options; no real Supervisor credentials.
    container = None
    try:
        container = docker("create", "-p", "127.0.0.1::80", "-p", "127.0.0.1::8099",
                           "--add-host", "host.docker.internal:host-gateway",
                           "-e", f"SUPERVISOR_API=http://host.docker.internal:{supervisor.server_port}",
                           "-e", "NO_PROXY=*", "-e", "no_proxy=*", args.image)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "options.json"
            path.write_text(json.dumps(options))
            docker("cp", str(path), f"{container}:/data/options.json")
        docker("start", container)
        ports = json.loads(docker("inspect", container))[0]["NetworkSettings"]["Ports"]
        admin = "http://127.0.0.1:" + ports["8099/tcp"][0]["HostPort"]
        proxy = "http://127.0.0.1:" + ports["80/tcp"][0]["HostPort"]

        def version_at(base, host=None):
            status, body = request(base, "/features", host=host)
            return status == 200 and json.loads(body)["version"] == args.expected_version

        eventually(lambda: version_at(admin), "admin startup and packaged version")
        status, body = request(admin, "/")
        assert status == 200 and b"<!doctype html>" in body.lower(), "Admin UI failed"
        payload = {"name": "SmokeTest", "domain": "smoke.example.com",
                   "backend": {"url": "http://127.0.0.1:8099"}, "https": False, "forcetls": False}
        status, body = request(admin, "/config/new", "POST", payload)
        assert status == 200, (status, body)
        result = json.loads(body)
        assert result["backend"]["healthy"], result
        route_id = result["id"]
        eventually(lambda: version_at(proxy, "smoke.example.com"), "Traefik to serve the created route")
        status, body = request(admin, "/config/" + route_id, "DELETE")
        assert status == 200, (status, body)
        eventually(lambda: request(proxy, "/features", host="smoke.example.com")[0] == 404,
                   "Traefik to remove the deleted route")
        assert json.loads(docker("inspect", container))[0]["State"]["Running"], "Add-on stopped"
        print(f"PASS: {args.image}: boot, UI, {args.expected_version}, route creation, proxying and deletion")
    except BaseException:
        if container:
            print(docker("logs", "--tail", "100", container))
        raise
    finally:
        if container:
            docker("rm", "-f", "-v", container)
        supervisor.shutdown()
        supervisor.server_close()


if __name__ == "__main__":
    main()
