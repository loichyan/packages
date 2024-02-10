_just := quote(just_executable()) + ' --justfile=' + quote(justfile())
_setup_bash := 'set -euo pipefail'
outdir := justfile_directory() / 'rpmbuild/SOURCES'
author := 'Loi Chyan <loichyan@foxmail.com>'
image := 'fedora-rpmbuild:39'

set shell := ["/usr/bin/env", "bash", "-euo", "pipefail", "-c"]
set positional-arguments := true
set ignore-comments := true
set export := true

_default:
    @{{ _just }} --list

date:
    @date -u +"%Y-%m-%dT%T.%3N"
    @date -u +"%a %d %b %T %Y"

update package version:
    #!/usr/bin/env bash
    {{ _setup_bash }}
    pkg={{ quote(package) }}
    version={{ quote(version) }}
    author={{ quote(author) }}

    date_spec="$(date -u +"%Y-%m-%dT%T.%3N")"
    date_chg="$(date -u -d"$date_spec" +"%a %d %b %T %Y")"
    sed -i \
        -e "s/\(%define version\) .*/\1 $version/" \
        -e "s/\(%define date\) .*/\1 $date_spec/" \
        "$pkg/$pkg.spec"
    sed -i \
        -e "1s/^/* $date_chg $author - $version-1\n\n/" \
        "$pkg/changelog"

build package:
    #!/usr/bin/env bash
    {{ _setup_bash }}
    pkg={{ quote(package) }}

    case "$pkg" in
    my*)
        rm rpmbuild/RPMS/*/"$pkg"*.rpm
        {{ _just }} docker rpmbuild -ba "/workspace/$pkg/$pkg.spec"
    ;;
    *)
        echo "not supported"
    ;;
    esac

docker *args="":
    docker run -it --rm --network=host \
        -v "$PWD:/workspace:Z" \
        -v "$PWD/rpmbuild:/root/rpmbuild:Z" \
        {{ quote(image) }} "${@}"

ci *args:
    @mkdir -p "{{ outdir }}"
    @./ci.py --outdir="$PWD/rpmbuild/SOURCES" "$@"
