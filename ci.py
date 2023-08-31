#!/usr/bin/env python3

from argparse import ArgumentParser
from functools import cached_property
from importlib import import_module
from lib import BasePackage
import logging as L
import typing as T


class App:
    @cached_property
    def cli(self):
        parser = ArgumentParser()
        for long in [
            "--ci",
            "--show-service",
            "--update-service",
            "--update",
            "--update-source",
            "--release",
            "--rebuild",
        ]:
            parser.add_argument(long, action="store_true")
        parser.add_argument("-a", "--all", action="store_true")
        parser.add_argument("-m", "--message", metavar="STRING")
        parser.add_argument("-o", "--outdir", metavar="PATH")
        parser.add_argument("package", nargs="*")
        return parser.parse_args()

    def run(self):
        args = self.cli
        if args.all:
            args.package = [
                "librime",
                "nerd-font-symbols",
                "nix-mount",
                "pop-launcher",
                "sarasa-gothic-fonts",
                "v2raya",
                "wezterm",
                "xray",
            ]
        packages: T.List[BasePackage] = []
        for pname in args.package:
            try:
                pmod = import_module(f"{pname}.package")
            except ModuleNotFoundError:
                raise RuntimeError(f"Package {pname} not found")
            packages.append(pmod.Package())

        for package in packages:
            if args.ci and package.update():
                package.update_source()
                package.release()
                package.rebuild()
            elif not args.ci:
                if args.show_service:
                    print(package.service)
                if args.update_service:
                    package.update_service(args.message)
                if args.update and package.update():
                    package.update()
                if args.update_source:
                    package.update_source(args.outdir)
                if args.release:
                    package.release(args.message)
                if args.rebuild:
                    package.rebuild()


if __name__ == "__main__":
    L.basicConfig(
        level=L.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    App().run()
