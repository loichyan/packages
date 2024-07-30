ARG FEDORA=40

FROM fedora-rpmbuild:${FEDORA} AS builder
ARG PACKAGE

COPY $PACKAGE /workspace
WORKDIR /workspace

RUN if grep -q '^BuildRequires:' "$PACKAGE.spec"; then \
        dnf builddep -y "$PACKAGE.spec" \
        && dnf clean all \
        && rm -rf /var/cache/dnf \
    ;fi

FROM builder as package
ARG PACKAGE

RUN rpmbuild -D 'debug_package %{nil}' -ba "$PACKAGE.spec"
