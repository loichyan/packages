set export := true
set ignore-comments := true
set positional-arguments := true
set shell := ["/usr/bin/env", "bash", "-euo", "pipefail", "-c"]

_just := quote(just_executable()) + " --justfile=" + quote(justfile())
_setup_bash := "set -euo pipefail"

_default:
    @command {{ _just }} --list

date:
    @date -u +"%Y-%m-%dT%T"
    @date -u +"%a %b %d %T %Y"

bump package version:
    #!/usr/bin/env bash
    command {{ _setup_bash }}

    date_spec="$(date -u +"%Y-%m-%dT%T")"
    date_chg="$(date -u +"%a %d %b %T %Y")"
    sed -i \
        -e "s/\(%define version\) .*/\1 $version/" \
        -e "s/\(%define date\) .*/\1 $date_spec/" \
        "$package/$package.spec"
    sed -i \
        -e "1s/^/* $date_chg $author - $version-1\n\n/" \
        "$package/changelog"

author := "Loi Chyan <loichyan@foxmail.com>"
fedora := "41"
outdir := justfile_directory() / "rpmbuild/SOURCES"

build package: build-image
    @set -x; docker build --network=host -f package.dockerfile \
        -v "$PWD/rpmbuild:/root/rpmbuild:Z" \
        --build-arg FEDORA="$fedora" \
        --build-arg PACKAGE="$package"

build-image:
    @set -x; docker build --network=host -f fedora.dockerfile \
        --build-arg FEDORA="$fedora" \
        -t "fedora-rpmbuild:$fedora"

clean-rpm:
    rm rpmbuild/RPMS/*/*.rpm
    rm rpmbuild/SRPMS/*.rpm

run-image *args:
    @set -x; docker run -it --rm --network=host \
        -v "$PWD:/workspace:Z" \
        -v "$PWD/rpmbuild:/root/rpmbuild:Z" \
        "fedora-rpmbuild:$fedora" "${@}"

ci *args:
    @mkdir -p "$outdir"
    ./ci.py --outdir="$PWD/rpmbuild/SOURCES" "$@"
