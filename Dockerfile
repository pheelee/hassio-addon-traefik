ARG BUILD_FROM
FROM $BUILD_FROM

EXPOSE 80
EXPOSE 443

ENV LANG C.UTF-8

# Get Traefik Release
RUN apk --no-cache add ca-certificates tzdata
RUN set -ex; \
        apkArch="$(apk --print-arch)"; \
        case "$apkArch" in \
                armhf) arch='armv6' ;; \
                armv7) arch='armv7' ;; \
                aarch64) arch='arm64' ;; \
                x86_64) arch='amd64' ;; \
                *) echo >&2 "error: unsupported architecture: $apkArch"; exit 1 ;; \
        esac; \
        wget --quiet -O /tmp/traefik.tar.gz "https://github.com/containous/traefik/releases/download/v2.3.4/traefik_v2.3.4_linux_$arch.tar.gz"; \
        tar xzvf /tmp/traefik.tar.gz -C /usr/local/bin traefik; \
        rm -f /tmp/traefik.tar.gz; \
        chmod +x /usr/local/bin/traefik

# Get Traefik-Admin Release
RUN set -ex; \
        apkArch="$(apk --print-arch)"; \
        case "$apkArch" in \
                armhf) arch='armv6' ;; \
                armv7) arch='armv7' ;; \
                aarch64) arch='arm64' ;; \
                x86_64) arch='amd64' ;; \
                *) echo >&2 "error: unsupported architecture: $apkArch"; exit 1 ;; \
        esac; \
        wget --quiet -O /tmp/traefik-admin.tar.gz "https://github.com/pheelee/traefik-admin/releases/download/v0.5/traefik-admin-linux-$arch.tar.gz"; \
        mkdir -p /web; \
        tar xzvf /tmp/traefik-admin.tar.gz -C /web; \
        rm -f /tmp/traefik-admin.tar.gz; \
        chmod +x /web/traefik-admin

WORKDIR /data

COPY rootfs /
