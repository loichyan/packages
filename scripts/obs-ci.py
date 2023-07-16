#!/usr/bin/env python3

from argparse import ArgumentParser
from datetime import datetime
from functools import cached_property
from textwrap import dedent
from xml.etree import ElementTree as ET
import logging as L
import os
import re
import requests as R
import typing as T


def require_env(key: str, default: T.Optional[str] = None):
    val = os.environ.get(key) or default
    assert val is not None, f"${key} must be specified"
    return val


class Global:
    @cached_property
    def PAT_SPEC_VTAG(self):
        return re.compile(r"^(%define vtag) (.+)$", flags=re.M)

    @cached_property
    def PAT_SPEC_VERSION(self):
        return re.compile(r"^(%define version) (.+)$", flags=re.M)

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
        return require_env("GH_TOKEN")

    @cached_property
    def OBS_TOKEN(self):
        return require_env("OBS_TOKEN")

    @cached_property
    def OBS_LOGIN(self):
        return require_env("OBS_LOGIN")

    @cached_property
    def OBS_PROJECT(self):
        return require_env("OBS_PROJECT")

    @cached_property
    def OBS_HOST(self):
        return require_env("OBS_HOST", "api.opensuse.org")

    @cached_property
    def COMMIT_USERNAME(self):
        return require_env("COMMIT_USERNAME", "github-actions[bot]")

    @cached_property
    def COMMIT_EMAIL(self):
        return require_env(
            "COMMIT_EMAIL", "github-actions[bot]@users.noreply.github.com"
        )

    @cached_property
    def GITHUB_OUTPUT(self):
        return require_env("GITHUB_OUTPUT")


G = Global()


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
        new_spec = G.PAT_SPEC_VTAG.sub(rf"\1 {new_vtag}", new_spec)
        new_spec = G.PAT_SPEC_VERSION.sub(rf"\1 {new_version}", new_spec)
        new_spec = G.PAT_SPEC_AUTORELEASE.sub(r"\1", new_spec)
        with open(self._spec_path, "w") as f:
            f.write(new_spec)
        L.info(f"Updating changelog of <{self.name}>")
        now = datetime.now().strftime("%c")
        with open(self._changelog_path, "r") as f:
            changelog = f.read()
        with open(self._changelog_path, "w") as f:
            changes = dedent(
                f"""\
                * {now} {G.COMMIT_USERNAME} <{G.COMMIT_EMAIL}> - {new_version}-1\n
                - Bump version tag to {new_vtag}\n
                """
            )
            f.write(changes + changelog)
        return new_version

    def rebuild(self):
        """
        Rebuilds this package.
        """
        L.info(f"Rebuilding <{self.name}>")
        self._obs_api(
            f"trigger/runservice",
            method="POST",
            authorization="token",
            params={"project": G.OBS_PROJECT, "package": self.name},
        )

    def update_service(self):
        """
        Updates services of this package.
        """
        service = dedent(
            f"""\
            <services>
                <service name="obs_scm">
                    <param name="scm">git</param>
                    <param name="url">https://github.com/loichyan/packages</param>
                    <param name="revision">main</param>
                    <param name="subdir">{self.name}</param>
                    <param name="filename">source</param>
                    <param name="without-version">true</param>
                </service>
                <service name="extract_file">
                    <param name="archive">_service:obs_scm:source.obscpio</param>
                    <param name="files">source/*</param>
                </service>
            </services>\
            """
        )
        self._obs_api(
            f"source/{G.OBS_PROJECT}/{self.name}/_service",
            method="PUT",
            headers={"Content-Type": "application/xml"},
            params="Update _service",
            data=service,
        )

    def _obs_api(
        self,
        path: str,
        method: T.Optional[str] = None,
        auth: T.Optional[T.Literal["login", "token"]] = None,
        **kwargs,
    ) -> ET.Element:
        url = f"{G.OBS_HOST}/{path}"
        L.info(f"Calling OBS API: {url}")
        if auth == None or auth == "login":
            authorization = f"Basic {G.OBS_LOGIN}"
        elif auth == "token":
            authorization = f"Token {G.OBS_TOKEN}"
        else:
            raise ValueError(f"Unsupported authorization method: '{auth}'")
        kwargs.update(
            dict(
                headers={
                    "Accept": "application/xml; charset=utf-8",
                    "Authorization": authorization,
                    **(kwargs.get("headers") or {}),
                },
            )
        )
        resp = R.request(method or "GET", f"https://{url}", **kwargs)
        tree = ET.fromstring(resp.text)
        if resp.status_code != 200:
            summary = tree.find("./status/summary")
            summary = summary.text if summary is not None else None
            raise RuntimeError(f"Cannot rebuild '{self.name}': {summary or resp.text}")
        return tree

    def _parse_version(self, vtag: str) -> T.Optional[str]:
        """
        Parses %version from %vtag.
        """
        mat = G.PAT_VERSION.match(vtag)
        if mat is not None:
            return mat[2]

    def _update_vtag(self, _: str) -> T.Optional[str]:
        """
        Fetches the new %vtag if no avaiable `None` should be returned.
        """
        L.warn(f"<{self.name}> cannot be updated")
        return None


class GhPackage(Package):
    def __init__(self, name: str, repo: str):
        super().__init__(name)
        self.repo = repo

    def _parse_version(self, vtag: str) -> T.Optional[str]:
        mat = G.PAT_VERSION.match(vtag)
        if mat is not None:
            return mat[1]

    def _update_vtag(self, vtag: str) -> T.Optional[str]:
        L.info(f"Fetching the latest release of {self.repo}")
        resp = self._gh_api(f"https://api.github.com/repos/{self.repo}/releases/latest")
        latest_vtag = resp["tag_name"]
        if latest_vtag != vtag:
            return latest_vtag

    def _gh_api(self, url: str, method: T.Optional[str] = None, **kwargs) -> T.Any:
        resp = R.request(
            method or "GET",
            url,
            **{
                "headers": {
                    "Authorization": f"Bearer {G.GH_TOKEN}",
                    "Content-Type": "application/json",
                    **(kwargs.get("params") or {}),
                },
                **kwargs,
            },
        )
        return resp.json()


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


def gh_output(key: str, value: str):
    with open(G.GITHUB_OUTPUT, "a") as f:
        f.write(f"{key}={value}")


def cli():
    parser = ArgumentParser()
    parser.add_argument("-p", "--package", action="append")
    parser.add_argument("-a", "--all", action="store_true")
    parser.add_argument("--ci", action="store_true")
    parser.add_argument("--update-service", action="store_true")
    parser.add_argument("--update", action="store_true")
    parser.add_argument("--rebuild", action="store_true")
    return parser.parse_args()


def main():
    L.basicConfig(level=L.INFO)
    args = cli()
    for pname in PACKAGES.keys() if args.all else args.package:
        package = PACKAGES.get(pname)
        assert package is not None, f"<{pname}> is not defined"
        if args.update_service:
            package.update_service()
        updated = None
        if args.update:
            new_version = package.update()
            if new_version is None:
                updated = False
            else:
                updated = True
                if args.ci:
                    gh_output("new_version", new_version)
        if updated != False and args.rebuild:
            package.rebuild()


main()
