_just := quote(just_executable()) + ' --justfile=' + quote(justfile())
outdir := justfile_directory() / 'rpmbuild/SOURCES'

set shell := ["/usr/bin/env", "bash", "-euo", "pipefail", "-c"]
set positional-arguments := true
set ignore-comments := true

_default:
    @{{ _just }} --list

date:
    @date -u +"%Y-%m-%dT%T.%3N"
    @date -u +"%a %d %b %T %Y"

docker image="fedora-rpmbuild:39":
    docker run -it --rm --network=host \
        -v "$PWD:/workspace:Z" \
        -v "$PWD/rpmbuild:/root/rpmbuild:Z" \
        "{{ image }}"

ci *args:
    @mkdir -p "{{ outdir }}"
    @./ci.py --outdir="$PWD/rpmbuild/SOURCES" "$@"
