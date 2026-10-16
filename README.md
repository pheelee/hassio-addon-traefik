# Traefik

[![GitHub Release][releases-shield]][releases]
![Project Stage][project-stage-shield]
[![License][license-shield]](LICENSE.md)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]

![Project Maintenance][maintenance-shield]

Create reverse proxy configs via web interface!

## About

Traefik is a reverse proxy with a strong focus on container orchestration plaforms. Beside that it also supports
dynamic configuration via file input. This addon provides a beautiful web interface to create the
dynamic configuration for you.

By using this addon you agree to the TOS of lets encrypt.

### Features

- 🔒 HTTPS by default (provided by lets encrypt)
- 🔒 HTTP to HTTPS redirect
- 🔒 HSTS
- 🔠 Custom request headers
- 🗝️ Basic auth
- 🗝️ SSO using homeassistant api
- 🚪 IP restriction

## Configuration

```
loglevel: error
email: webmaster@example.ch
authEndpoint: 'https://hass.example.com/auth/authorize'
cookieSecret: aVerySecureStringHere
insecureSkipVerify: false
environment:
  - DNS_PROVIDER=cloudflare
  - CF_DNS_API_TOKEN=12345
hosts:
  - 192.168.1.1 foo.example.com
rootCAs: []
```

### Option: `loglevel`

The `log_level` option controls the level of log output by the addon and can
be changed to be more or less verbose, which might be useful when you are
dealing with an unknown issue. Possible values are:

- `trace`: Show every detail, like all called internal functions.
- `debug`: Shows detailed debug information.
- `info`: Normal (usually) interesting events.
- `warning`: Exceptional occurrences that are not errors.
- `error`: Runtime errors that do not require immediate action.
- `fatal`: Something went terribly wrong. Add-on becomes unusable.

Please note that each level automatically includes log messages from a
more severe level, e.g., `debug` also shows `info` messages. By default,
the `log_level` is set to `error`, which is the recommended setting unless
you are troubleshooting.

### Option: `email`

The `email` option is required for the registration with the lets encrypt service.

### Option: `httpreq`

**removed**
This option sets the necessary variables and cert resolver to dns01.
Please refer the official documentation from traefik for further details https://doc.traefik.io/traefik/https/acme/#dnschallenge

### Option: `authEndpoint`

This option enables the forward auth feature. With this feature you can secure any proxy entry with the homeassistant login system.
It also works as single sign on (SSO) solution for all proxy entries sharing the forward auth config.

### Option: `cookieSecret`

This should be a very random value used for encryption of the cookies for forward auth.

### Option: `insecureSkipVerify`

Skip verification of ssl certs on backends. Useful if you proxy to a tls/ssl backend with a self signed certificate
Try to leave this settings to `false` and provide necessary root CAs.
Please refer the official documentation from traefik for further details https://doc.traefik.io/traefik/routing/overview/#insecureskipverify

### Option: `environment`

Sets the specified environment variables. This can be used to provider information for the dns challenge provider.
Use the variable `DNS_PROVIDER` to specify the provider.
More information can be found at https://doc.traefik.io/traefik/https/acme/#providers

```
DNS_PROVIDER=cloudflare
CF_DNS_API_TOKEN=12345
```

### Option: `hosts`

Writes the entries to the hosts file.

```
192.168.1.1 foo.example.com
```

### Option: `rootCAs`

Specifies a list of root CAs as base64 strings to import in traefik.

## Development and dependency updates

The source layout, CI, maintenance and deployment follow Home Assistant Community
Apps. Add-on files live in `traefik/`; source `config.yaml` uses `version: dev`.
Install published versions through [the Home Assistant catalog][repository],
which supplies the actual version and GHCR image reference.

This repository owns Traefik, published traefik-admin releases, the community
base image and GitHub Actions. The admin repository independently owns its Go
and frontend dependencies. Renovate tracks releases through annotated Dockerfile
arguments, groups base updates and pins Actions to commits. Like the community
repositories, compatible upstream and base updates can automerge after the
full PR check suite (including the `Test build` aggregate) passes. Major updates require dashboard approval.
Renovate performs the merge after checks; platform automerge is disabled to avoid
merging before CI has reported its result.

`traefik/build.yaml` and the Dockerfile use the community base version. Base
references use version tags, matching the community linter's schema. Both
upstream binary archives must pass their publisher's SHA-256 manifest before
extraction. This packaging change does not resolve advisories in Traefik 2.9.6;
its upgrade remains a separate compatibility task.

### Validation

CI directly calls pinned `hassio-addons/workflows` `app-ci.yaml`: the Home
Assistant app linter in community mode, Hadolint, JSON lint, ShellCheck including
extensionless s6 scripts, yamllint, Prettier, zizmor, dependency review and native
amd64/arm64 builds. Additional tests reject invalid checksums and release metadata,
validate packaged image labels, boot the add-on and create/delete a real route
through Traefik. These tests use generated options and a minimal Supervisor API
fixture; they do not issue ACME certificates or test external SSO or real ingress.

ARMv7 is retired in this release, matching the supported community pipeline and
current Home Assistant architectures. Users of 32-bit installations must migrate
to a supported 64-bit installation before upgrading this add-on.

```sh
python3 -m pip install -r requirements-dev.txt
python3 -m unittest discover -s tests -v
base=$(python3 scripts/image-metadata.py amd64 | sed -n 's/^base=//p')
docker buildx build --load --build-arg BUILD_FROM="$base" \
  --build-arg BUILD_ARCH=amd64 --build-arg BUILD_VERSION=dev \
  -t traefik-addon-test:amd64 traefik
python3 scripts/check-image-metadata.py traefik-addon-test:amd64 amd64 dev
admin_version=$(python3 scripts/image-metadata.py amd64 | sed -n 's/^admin_version=//p')
python3 scripts/smoke-test.py traefik-addon-test:amd64 --expected-version "$admin_version"
```

Use `aarch64`, its configured base, and `--platform linux/arm64` for arm64. In an
environment with a private HTTPS proxy CA, pass
`--secret id=build_ca,src=/path/to/trusted-ca-bundle.pem` to the build; that CA is
available only during downloads and is absent from the final image.

### Deployment and maintenance

The pinned community `app-deploy.yaml` runs after both community CI and our
runtime tests pass. It publishes:

- `ghcr.io/pheelee/traefik/{arch}:<version>` for each supported architecture;
- `ghcr.io/pheelee/traefik:<version>` as a multi-architecture manifest;
- `edge` aliases on pushes to `main`, `beta` aliases for GitHub prereleases,
  and `stable` aliases for published stable releases.

Edge versions use the short source commit; release versions come from the GitHub
tag, without its optional `v` prefix. The source config stays at `dev`. Release Drafter proposes the next
version from PR labels. Publish its tag as a stable release or use a prerelease
tag such as `v1.0.0-rc.1` for a beta. An admin release alone does not release the add-on.

The deployment workflow uses `GITHUB_TOKEN` with `packages: write` for GHCR;
Docker Hub credentials are no longer used. After first publication, make the
Traefik GHCR packages public so Home Assistant can pull without authentication.
The repository owner must set this in GitHub package settings.

The community deployment dispatches catalog updates to `pheelee/hassio` using a
`DISPATCH_TOKEN` repository secret with Contents write access to that repository.
The companion catalog workflow prepares source files as data in a read-only job,
rejecting symlinks, path escapes and source templates. A separate publisher
validates the candidate and uses the short-lived repository `GITHUB_TOKEN` only
for its final push. No `UPDATER_TOKEN` PAT or community updater library is used;
remove/revoke a PAT created solely for that obsolete secret. Stable releases
refresh stable and beta; prereleases refresh beta; main builds refresh edge.
Merge [the catalog integration PR](https://github.com/pheelee/hassio/pull/2)
and configure the source-side `DISPATCH_TOKEN` before deploying this pipeline.
The catalog listens for dispatches, not its own pushes, preventing an updater loop.

Pinned community workflows also synchronize labels, enforce PR category labels
and maintain a release draft on `main`. `.github/release-drafter.yml` defines
release categories and version resolution; it does not publish releases.
Checkout credentials are not persisted, superseded CI is cancelled and deployments
are serialized by the shared workflow. Add a category label such as `ci`,
`maintenance`, `bugfix` or `dependencies` to each PR.

## License

MIT License

Copyright (c) 2021-2022 Philipp Ritter

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

[aarch64-shield]: https://img.shields.io/badge/aarch64-yes-green.svg
[amd64-shield]: https://img.shields.io/badge/amd64-yes-green.svg
[license-shield]: https://img.shields.io/github/license/pheelee/hassio-addon-traefik.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2026.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-stable-green.svg
[releases-shield]: https://img.shields.io/github/release/pheelee/hassio-addon-traefik.svg
[releases]: https://github.com/pheelee/hassio-addon-traefik/releases
[repository]: https://github.com/pheelee/hassio
