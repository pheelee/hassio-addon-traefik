ARG BUILD_FROM=ghcr.io/hassio-addons/base:21.0.8
# BUILD_FROM is versioned above and in build.yaml.
# hadolint ignore=DL3006
FROM ${BUILD_FROM}

# renovate: datasource=github-releases depName=traefik/traefik
ARG TRAEFIK_VERSION=2.11.60
# renovate: datasource=github-releases depName=pheelee/traefik-admin
ARG TRAEFIK_ADMIN_VERSION=0.5.3

EXPOSE 80 443
ENV LANG=C.UTF-8

# The Home Assistant base supplies CA certificates, curl, tzdata, Bashio and s6.
COPY scripts/verify-sha256.sh /tmp/verify-sha256.sh
# Downloads and cleanup stay in one layer.
# hadolint ignore=DL3003
RUN --mount=type=secret,id=build_ca \
    set -eu; \
    if [ -f /run/secrets/build_ca ]; then export CURL_CA_BUNDLE=/run/secrets/build_ca; fi; \
    case "$(apk --print-arch)" in \
        aarch64) arch=arm64 ;; \
        x86_64) arch=amd64 ;; \
        *) echo 'Unsupported architecture' >&2; exit 1 ;; \
    esac; \
    mkdir /tmp/releases; cd /tmp/releases; \
    archive="traefik_v${TRAEFIK_VERSION}_linux_${arch}.tar.gz"; \
    release="https://github.com/traefik/traefik/releases/download/v${TRAEFIK_VERSION}"; \
    curl --fail --location --retry 3 --output "$archive" "$release/$archive"; \
    curl --fail --location --retry 3 --output checksums.txt "$release/traefik_v${TRAEFIK_VERSION}_checksums.txt"; \
    sh /tmp/verify-sha256.sh checksums.txt "$archive"; \
    tar -xzf "$archive" -C /usr/local/bin traefik; \
    archive="traefik-admin-linux-${arch}.tar.gz"; \
    release="https://github.com/pheelee/traefik-admin/releases/download/v${TRAEFIK_ADMIN_VERSION}"; \
    curl --fail --location --retry 3 --output "$archive" "$release/$archive"; \
    curl --fail --location --retry 3 --output SHA256SUMS "$release/SHA256SUMS"; \
    sh /tmp/verify-sha256.sh SHA256SUMS "$archive"; \
    mkdir /web; tar -xzf "$archive" -C /web traefik-admin; \
    chmod 755 /usr/local/bin/traefik /web/traefik-admin; \
    cd /; rm -rf /tmp/releases /tmp/verify-sha256.sh

WORKDIR /data
COPY rootfs /
RUN chmod 755 /etc/cont-init.d/01-hosts /etc/services.d/*/run

# Match the metadata contract used by Home Assistant Community Apps.
ARG BUILD_ARCH=amd64
ARG BUILD_DATE=unknown
ARG BUILD_DESCRIPTION="Reverse Proxy for Web Services"
ARG BUILD_NAME=Traefik
ARG BUILD_REF=unknown
ARG BUILD_REPOSITORY=pheelee/hassio-addon-traefik
ARG BUILD_VERSION=dev
LABEL \
    io.hass.name="${BUILD_NAME}" \
    io.hass.description="${BUILD_DESCRIPTION}" \
    io.hass.arch="${BUILD_ARCH}" \
    io.hass.type="addon" \
    io.hass.version="${BUILD_VERSION}" \
    maintainer="pheelee <pri@irbe.ch>" \
    org.opencontainers.image.title="${BUILD_NAME}" \
    org.opencontainers.image.description="${BUILD_DESCRIPTION}" \
    org.opencontainers.image.vendor="pheelee" \
    org.opencontainers.image.authors="pheelee <pri@irbe.ch>" \
    org.opencontainers.image.licenses="MIT" \
    org.opencontainers.image.url="https://github.com/${BUILD_REPOSITORY}" \
    org.opencontainers.image.source="https://github.com/${BUILD_REPOSITORY}" \
    org.opencontainers.image.documentation="https://github.com/${BUILD_REPOSITORY}/blob/main/README.md" \
    org.opencontainers.image.created="${BUILD_DATE}" \
    org.opencontainers.image.revision="${BUILD_REF}" \
    org.opencontainers.image.version="${BUILD_VERSION}"
