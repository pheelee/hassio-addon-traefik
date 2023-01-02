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