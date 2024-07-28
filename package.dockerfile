ARG FEDORA=40

FROM fedora-rpmbuild:${FEDORA} AS builder
ARG PACKAGE

COPY $PACKAGE /workspace
WORKDIR /workspace

RUN dnf builddep -y "$PACKAGE.spec" \
    && dnf clean all \
    && rm -rf /var/cache/dnf

FROM builder as package
ARG PACKAGE

RUN rpmbuild -D 'debug_package %{nil}' -ba "$PACKAGE.spec"
