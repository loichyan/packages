#!/usr/bin/env bash
set -euxo pipefail

RPMBUILD="${RPMBUILD:-~/rpmbuild}"
SOURCES_DIR="$RPMBUILD/SOURCES"

if grep -q '^BuildRequires:' "$PACKAGE.spec"; then
    dnf builddep -y "$PACKAGE.spec"
    dnf clean all
    rm -rf /var/cache/dnf
fi

mkdir -p "$SOURCES_DIR"
while IFS= read -r src; do
    cp "$src" "$SOURCES_DIR"
done < <(sed -n 's/^Source[[:digit:]]:\s\+\(.\+\)/\1/p' "$PACKAGE.spec")
