FROM fedora:39 AS base

FROM base
RUN dnf install -y rpm-build rpmdevtools 'dnf-command(builddep)' && \
    dnf clean all && \
    rm -rf /var/cache/dnf
