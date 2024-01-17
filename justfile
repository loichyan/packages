set shell := ["/usr/bin/env", "bash", "-euo", "pipefail", "-c"]
set positional-arguments := true
set ignore-comments := true

date:
    @date -u +"%Y-%m-%dT%T.%3N"
    @date -u +"%a %d %b %T %Y"

docker image="fedora-rpmbuild:39":
    docker run -it --rm --network=host \
        -v "$PWD:/workspace:Z" \
        -v "$PWD/rpmbuild:/root/rpmbuild:Z" \
        "{{ image }}"

ci *args:
    ./ci.py --outdir="$PWD/SOURCES" "$@"
