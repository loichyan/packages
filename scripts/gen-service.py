#!/usr/bin/env python3

# Generate _service file used by an OBS package to fetch the source.

from argparse import ArgumentParser
from textwrap import dedent


def cli():
    parser = ArgumentParser()
    parser.add_argument("-p", "--package", required=True)
    return parser.parse_args()


def main():
    args = cli()
    package = args.package
    service = dedent(
        f"""\
        <services>
          <service name="tar_scm">
            <param name="scm">git</param>
            <param name="url">https://github.com/loichyan/packages</param>
            <param name="revision">main</param>
            <param name="subdir">{package}</param>
            <param name="filename">source</param>
            <param name="without-version">true</param>
          </service>
          <service name="extract_file">
            <param name="archive">_service:tar_scm:source.tar</param>
            <param name="files">source/*</param>
          </service>
          <service name="recompress">
            <param name="file">_service:tar_scm:source.tar</param>
            <param name="compression">gz</param>
          </service>
        </services>\
        """
    )
    print(service)


main()
