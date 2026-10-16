## Unreleased

### Breaking changes

- Retire ARMv7; amd64 and aarch64 remain supported.
- Move images to GHCR and adopt community edge/beta/stable release channels.

### Changes

- Adopt the pinned community CI/deployment, community base, lint/security checks,
  selective Renovate automerge, release drafting, label automation and workflow hygiene.
- Set and verify add-on/OCI image metadata instead of inheriting base metadata.

- Update traefik-admin to v0.5.3 with security fixes and self-hosted icons.
- Verify Traefik and admin release checksums before installing binaries.
- Track upstream releases, pinned Home Assistant bases and GitHub Actions with Renovate.
- Fix startup with no DNS provider and select the admin certificate resolver from current options.
- Build and smoke-test all supported architectures before publishing images.

## v0.5.3

### 🛠️ Fixes

### 🔨 Changes

- Bump Traefik to v2.9.6

## v0.5.2

### 🛠️ Fixes

- add init:false to config to support s6 3.x

### 🔨 Changes

- Bump Traefik to v2.7.0
- removed httpreq config options in favor of environment where any arbitrary variable can be set

## v0.5.1

### 🛠️ Fixes

- fix webinterface startup error if no authEndpoint is specified
- add hosts entries

## v0.5.0

### 🔨 Changes

- add SSO using traefiks forward auth and the homeassistant auth api
- UI overhaul
- manually add hosts entries
- toast notifications

## v0.4.1

### 🛠️ Fixes

- support multiple root ca's from config

## v0.4.0

### 🔨 Changes

- add HSTS to configs
- add IP restriction to configs
- use dns as cert resolver
- bump traefik to 2.3.4
