# Companion catalog integration

`hassio-catalog.patch` contains the prepared commits for `pheelee/hassio`.
It adds the community repository-updater integration, stable/beta/edge dispatch
handling, tests and token/setup documentation. Current catalog versions/images
remain unchanged; existing entries only gain missing source URL metadata.

This environment currently receives HTTP 403 when pushing a branch or creating a
Git ref in that repository. Once access is granted, the companion branch/PR can
be published. Alternatively, apply the patch in a checkout of `pheelee/hassio`
on a new branch with `git am /path/to/hassio-catalog.patch`, then open a PR.

Merge that catalog PR first and configure `UPDATER_TOKEN` there plus
`DISPATCH_TOKEN` in this source repository, as described in the patched
`TRAEFIK-MAINTENANCE.md`. The source deployment preflight requires the receiver
and dispatch token before any images are published. GHCR package visibility
must be public before Home Assistant users can pull the new images.
