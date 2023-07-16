#!/usr/bin/env python3

from argparse import ArgumentParser
from datetime import datetime
from functools import cached_property
from xml.etree import ElementTree as ET
import logging as L
import os
import re
import requests as R
import typing as T


class Global:
    @cached_property
    def PAT_SPEC_VTAG(self):
        return re.compile(r"^(%define vtag )(.+)$", flags=re.M)

    @cached_property
    def PAT_SPEC_VERSION(self):
        return re.compile(r"^(%define version )(.+)$", flags=re.M)

    @cached_property
    def PAT_SPEC_AUTORELEASE(self):
        return re.compile(r"^(Release: +%autorelease)(.*)$", flags=re.M)

    @cached_property
    def PAT_VERSION(self):
        return re.compile(r"^v(.+)$")

    @cached_property
    def PAT_WEZTERM_VERSION(self):
        return re.compile(r"^(\d+)-(\d+)-([0-9a-f]+)$")

    @cached_property
    def GH_TOKEN(self):
        val = os.environ.get("GH_TOKEN")
        assert val is not None, "$GH_TOKEN must be specified"
        return val

    @cached_property
    def OBS_TOKEN(self):
        val = os.environ.get("OBS_TOKEN")
        assert val is not None, "$OBS_TOKEN must be specified"
        return val

    @cached_property
    def OBS_PROJECT(self):
        val = os.environ.get("OBS_PROJECT")
        assert val is not None, "$OBS_PROJECT must be specified"
        return val

    @cached_property
    def OBS_HOST(self):
        return os.environ.get("OBS_HOST") or "api.opensuse.org"

    @cached_property
    def COMMIT_USERNAME(self):
        return os.environ.get("COMMIT_USERNAME") or "github-actions[bot]"

    @cached_property
    def COMMIT_EMAIL(self):
        return (
            os.environ.get("COMMIT_EMAIL")
            or "github-actions[bot]@users.noreply.github.com"
        )


G = Global()


class Response:
    def __init__(self, text: str):
        self.text = text

    @cached_property
    def tree(self) -> ET.Element:
        return ET.fromstring(self.text)

    @cached_property
    def status_code(self) -> str:
        code = self.tree.get("code")
        assert code is not None, "Cannot parse status.code from the response"
        return code

    @cached_property
    def status_summary(self) -> str:
        summary = self.tree.find("./summary")
        summary = summary.text if summary is not None else None
        assert summary is not None, "Cannot parse status.summary from the response"
        return summary


class Package:
    def __init__(self, name: str):
        self.name = name

    @cached_property
    def _spec_path(self) -> str:
        return f"{self.name}/{self.name}.spec"

    @cached_property
    def _changelog_path(self) -> str:
        return f"{self.name}/{self.name}.changes"

    @cached_property
    def _spec(self) -> str:
        with open(self._spec_path) as f:
            return f.read()

    @cached_property
    def vtag(self) -> str:
        mat = G.PAT_SPEC_VTAG.match(self._spec)
        assert mat is not None, "Cannot parse %vtag from the spec"
        return mat[2]

    def update(self) -> T.Optional[str]:
        """
        Updates this package.
        """
        new_vtag = self._update_vtag(self.vtag)
        if new_vtag is None:
            return
        L.info(f"Updating <{self.name}> to {new_vtag}")
        new_version = self._parse_version(new_vtag)
        new_spec = self._spec
        new_spec = G.PAT_SPEC_VTAG.sub(f"$1{new_vtag}", new_spec)
        new_spec = G.PAT_SPEC_VERSION.sub(f"$1{new_version}", new_spec)
        new_spec = G.PAT_SPEC_AUTORELEASE.sub("$1", new_spec)
        with open(self._spec_path, "w") as f:
            f.write(new_spec)
        L.info(f"Updating changelog of <{self.name}>")
        now = datetime.now().strftime("%c")
        changelog = (
            f"* {now} {G.COMMIT_USERNAME} <{G.COMMIT_EMAIL}> - {new_version}-1\n"
            f"- Bump version tag to {new_vtag}\n"
        )
        with open(self._changelog_path, "r") as f:
            changelog = changelog + "\n" + f.read()
        with open(self._changelog_path, "w") as f:
            f.write(changelog)
        return new_vtag

    def rebuild(self):
        """
        Rebuilds this package.
        """
        L.info(f"Rebuilding <{self.name}>")
        resp = R.post(
            f"https://{G.OBS_HOST}/trigger/runservice",
            params={
                "project": G.OBS_PROJECT,
                "package": self.name,
            },
            headers={
                "Authorization": f"Token {G.OBS_TOKEN}",
                "Accept": "application/xml; charset=utf-8",
                "Content-Type": "application/json",
            },
        )
        resp = Response(resp.text)
        if resp.status_code != "ok":
            raise RuntimeError(f"Cannot rebuild '{self.name}': {resp.status_summary}")

    def _parse_version(self, vtag: str) -> T.Optional[str]:
        """
        Parses %version from %vtag.
        """
        mat = G.PAT_VERSION.match(vtag)
        if mat is not None:
            return mat[2]

    def _update_vtag(self, vtag: str) -> T.Optional[str]:
        """
        Fetches the new %vtag if no avaiable `None` should be returned.
        """
        raise RuntimeError(f"<{self.name}> cannot be updated")


class GhPackage(Package):
    def __init__(self, name: str, repo: str):
        super().__init__(name)
        self.repo = repo

    def _parse_version(self, vtag: str) -> T.Optional[str]:
        mat = G.PAT_VERSION.match(vtag)
        if mat is not None:
            return mat[1]

    def _update_vtag(self, vtag: str) -> T.Optional[str]:
        resp = R.get(
            f"https://api.github.com/repos/{self.repo}/latest",
            headers={
                "Authorization": f"Bearer {G.GH_TOKEN}",
                "Content-Type": "application/json",
            },
        )
        json = resp.json()
        latest_vtag = json["tag_name"]
        if latest_vtag != vtag:
            return latest_vtag


class Wezterm(GhPackage):
    def _parse_version(self, vtag: str) -> T.Optional[str]:
        mat = G.PAT_WEZTERM_VERSION.match(vtag)
        if mat is not None:
            return mat[1]


PACKAGES: T.Dict[str, Package] = {
    "nix-mount": Package("nix-mount"),
    "sarasa-gothic-fonts": GhPackage("sarasa-gothic-fonts", "be5invis/Sarasa-Gothic"),
    "symbols-nerd-fonts": GhPackage("symbols-nerd-fonts", "ryanoasis/nerd-fonts"),
    "wezterm": Wezterm("wezterm", "wez/wezterm"),
}


def cli():
    parser = ArgumentParser()
    parser.add_argument("-p", "--package", action="append")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--rebuild", action="store_true")
    return parser.parse_args()


def main():
    args = cli()
    for pname in args.package:
        package = PACKAGES.get(pname)
        assert package is not None, f"<{pname}> is not defined"
        updated = None
        if args.update and package.update() is not None:
            if package.update() is not None:
                updated = False
            else:
                updated = True
        if updated != False and args.rebuild:
            package.rebuild()


main()
