#!/bin/sh
# Verify only the requested asset; never silently accept missing/duplicate entries.
set -eu
manifest=$1
archive=$2
case "$archive" in ''|*[!a-zA-Z0-9._-]*) echo 'Invalid archive filename' >&2; exit 1 ;; esac
digest=$(awk -v asset="$archive" '
    { name=$2; sub(/^\*/, "", name) }
    name == asset {
        count++
        if (NF != 2 || length($1) != 64 || $1 ~ /[^a-fA-F0-9]/) invalid=1
        hash=$1
    }
    END {
        if (count != 1 || invalid) exit 1
        print hash
    }
' "$manifest") || { echo "Missing, duplicate or invalid checksum for $archive" >&2; exit 1; }
printf '%s  %s\n' "$digest" "$archive" | sha256sum -c -
