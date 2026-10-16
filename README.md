# Traefik

[![GitHub Release][releases-shield]][releases]
![Project Stage][project-stage-shield]
[![License][license-shield]](LICENSE.md)

![Supports aarch64 Architecture][aarch64-shield]
![Supports amd64 Architecture][amd64-shield]
![Supports armv7 Architecture][armv7-shield]

![Project Maintenance][maintenance-shield]


Create reverse proxy configs via web interface!

## About

Traefik is a reverse proxy with a strong focus on container orchestration plaforms. Beside that it also supports
dynamic configuration via file input. This addon provides a beautiful web interface to create the
dynamic configuration for you.

By using this addon you agree to the TOS of lets encrypt.

### Features

* 🔒 HTTPS by default (provided by lets encrypt)
* 🔒 HTTP to HTTPS redirect
* 🔒 HSTS
* 🔠 Custom request headers
* 🗝️ Basic auth
* 🗝️ SSO using homeassistant api
* 🚪 IP restriction

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
### Option: ```loglevel```
The `log_level` option controls the level of log output by the addon and can
be changed to be more or less verbose, which might be useful when you are
dealing with an unknown issue. Possible values are:

- `trace`: Show every detail, like all called internal functions.
- `debug`: Shows detailed debug information.
- `info`: Normal (usually) interesting events.
- `warning`: Exceptional occurrences that are not errors.
- `error`:  Runtime errors that do not require immediate action.
- `fatal`: Something went terribly wrong. Add-on becomes unusable.

Please note that each level automatically includes log messages from a
more severe level, e.g., `debug` also shows `info` messages. By default,
the `log_level` is set to `error`, which is the recommended setting unless
you are troubleshooting.

### Option: ```email```
The `email` option is required for the registration with the lets encrypt service.

### Option: ```httpreq```
**removed**
This option sets the necessary variables and cert resolver to dns01.
Please refer the official documentation from traefik for further details https://doc.traefik.io/traefik/https/acme/#dnschallenge

### Option: ```authEndpoint```
This option enables the forward auth feature. With this feature you can secure any proxy entry with the homeassistant login system.
It also works as single sign on (SSO) solution for all proxy entries sharing the forward auth config.

### Option: ```cookieSecret```
This should be a very random value used for encryption of the cookies for forward auth.

### Option: ```insecureSkipVerify```
Skip verification of ssl certs on backends. Useful if you proxy to a tls/ssl backend with a self signed certificate
Try to leave this settings to `false` and provide necessary root CAs.
Please refer the official documentation from traefik for further details https://doc.traefik.io/traefik/routing/overview/#insecureskipverify

### Option: ```environment```
Sets the specified environment variables. This can be used to provider information for the dns challenge provider.
Use the variable ```DNS_PROVIDER``` to specify the provider.
More information can be found at https://doc.traefik.io/traefik/https/acme/#providers

```
DNS_PROVIDER=cloudflare
CF_DNS_API_TOKEN=12345
```

### Option: ```hosts```
Writes the entries to the hosts file.
```
192.168.1.1 foo.example.com
```

### Option: ```rootCAs```
Specifies a list of root CAs as base64 strings to import in traefik.

## Development and dependency updates

This repository owns the packaged Traefik version, the released traefik-admin
version, Home Assistant base images and CI actions. Renovate tracks these in its
Dependency Dashboard and opens reviewable PRs; automerge is disabled and major
updates require dashboard approval. The admin repository independently owns its
Go and frontend dependencies. Only published admin releases are consumed here.

`Dockerfile` declares upstream release versions. Both archives must match their
publisher's SHA-256 manifest before extraction. `build.json` pins a base version
and digest for each supported architecture; Renovate groups their updates.
Architecture-specific bases preserve ARMv7 support, which is absent from the new
consolidated Home Assistant base image. CI must pass for every architecture when
updating these bases. Traefik remains on 2.9.6 pending a separate compatibility
and security upgrade; adding tracking does not resolve advisories in that version.

Run the checksum tests and build a native development image:

```sh
python3 -m unittest discover -s tests -v
base=$(python3 scripts/image-metadata.py amd64 | sed -n 's/^base=//p')
docker buildx build --load --build-arg BUILD_FROM="$base" -t traefik-addon-test:amd64 .
admin_version=$(python3 scripts/image-metadata.py amd64 | sed -n 's/^admin_version=//p')
python3 scripts/smoke-test.py traefik-addon-test:amd64 --expected-version "$admin_version"
```

Use `aarch64` / `linux/arm64` or `armv7` / `linux/arm/v7` with the corresponding
base and `--platform` to build another architecture. Cross-platform builds and
container tests require QEMU/binfmt support. In an environment with a private
HTTPS proxy CA, pass `--secret id=build_ca,src=/path/to/trusted-ca-bundle.pem` to
the build. This adds build-time trust without putting that CA in the final image.

The shared build workflow tests checksum rejection, boots each architecture's
image and verifies admin version, UI loading, backend health and route creation
and deletion through Traefik. A minimal Supervisor API fixture supplies test
options; no real Supervisor credentials are used. It uses native amd64/arm64 runners and emulates
ARMv7. These checks do not issue ACME certificates or exercise Home Assistant
Supervisor ingress or external SSO.

To release, update `config.json` and `CHANGELOG.md`, merge the reviewed PR, then
publish a GitHub release whose tag matches the add-on version (with an optional
`v` prefix). The publish workflow uses the same build and smoke tests before
pushing versioned Docker Hub images. It requires the existing
`DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN` repository secrets. An admin release
alone does not publish an add-on image.

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
[armv7-shield]: https://img.shields.io/badge/armv7-yes-green.svg
[license-shield]: https://img.shields.io/github/license/pheelee/hassio-addon-traefik.svg
[maintenance-shield]: https://img.shields.io/maintenance/yes/2024.svg
[project-stage-shield]: https://img.shields.io/badge/project%20stage-stable-green.svg
[releases-shield]: https://img.shields.io/github/release/pheelee/hassio-addon-traefik.svg
[releases]: https://github.com/pheelee/hassio-addon-traefik/releases
[repository]: https://github.com/pheelee/hassio

