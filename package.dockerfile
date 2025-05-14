ARG FEDORA=42

FROM fedora-rpmbuild:$FEDORA AS builder
ARG PACKAGE

WORKDIR /workspace
COPY $PACKAGE scripts .

RUN PACKAGE=$PACKAGE ./prepare-sources.sh

FROM builder as package
ARG PACKAGE

RUN rpmbuild -D 'debug_package %{nil}' -ba "$PACKAGE.spec"
