ARG FEDORA=41

FROM fedora:$FEDORA AS base

RUN dnf install -y \
    rpm-build \
    rpmdevtools \
    dnf-command\(builddep\) \
    && dnf clean all \
    && rm -rf /var/cache/dnf
