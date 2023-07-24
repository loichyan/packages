#!/usr/bin/env python3

from argparse import ArgumentParser
from datetime import datetime
from functools import cached_property
from subprocess import run
from xml.etree import ElementTree as ET
import logging as L
import os
import re
import requests as R
import typing as T


def git(*args: str):
    run(
        [
            "git",
            "-c",
            f"user.name={G.COMMIT_USERNAME}",
            "-c",
            f"user.email={G.COMMIT_EMAIL}",
            *args,
        ]
    )


def obs_api(
    path: str,
    method: T.Optional[str] = None,
    auth: T.Optional[T.Literal["login", "token"]] = None,
    **kwargs,
) -> ET.Element:
    """
    Calls OBS API.
    """
    L.info(f"Calling OBS API: {path}")
    if auth == None or auth == "login":
        authorization = f"Basic {G.OBS_LOGIN}"
    elif auth == "token":
        authorization = f"Token {G.OBS_TOKEN}"
    else:
        raise ValueError(f"Unsupported authorization method: '{auth}'")
    kwargs.update(
        {
            "headers": {
                "Accept": "application/xml; charset=utf-8",
                "Authorization": authorization,
                **(kwargs.get("headers") or {}),
            },
        }
    )
    resp = R.request(method or "GET", f"https://{G.OBS_HOST}{path}", **kwargs)
    tree = ET.fromstring(resp.text)
    if resp.status_code != 200:
        summary = tree.find("./status/summary")
        summary = summary.text if summary is not None else None
        raise RuntimeError(f"OBS API error: {summary or resp.text}")
    return tree


def gh_api(path: str, method: T.Optional[str] = None, **kwargs) -> T.Any:
    resp = R.request(
        method or "GET",
        f"https://api.github.com{path}",
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


def write(path: str, content: str):
    with open(path, "w") as f:
        f.write(content)


def read(path: str):
    with open(path, "r") as f:
        return f.read()


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
    def GH_TOKEN(self):
        return require_env("GH_TOKEN")

    @cached_property
    def GH_REPO(self):
        return require_env("GH_REPO", "loichyan/packages")

    @cached_property
    def COMMIT_USERNAME(self):
        return require_env("COMMIT_USERNAME", "github-actions")

    @cached_property
    def COMMIT_EMAIL(self):
        return require_env("COMMIT_EMAIL", "github-actions@github.com")

    @cached_property
    def PACKAGES(self) -> T.Dict[str, T.Callable[[], "Package"]]:
        return {
            "nix-mount": NixMount,
            "sarasa-gothic-fonts": SarasaGothicFonts,
            "symbols-nerd-fonts": SymbolsNerdFonts,
            "wezterm": Wezterm,
        }


G = Global()


class Package:
    def __init__(self, name: str):
        self.name = name

    @cached_property
    def _spec_path(self):
        return f"{self.name}/{self.name}.spec"

    @cached_property
    def _changelog_path(self):
        return f"{self.name}/{self.name}.changes"

    @cached_property
    def _manifest_path(self):
        return f"{self.name}/manifest"

    @cached_property
    def _spec(self):
        with open(self._spec_path) as f:
            return f.read()

    @cached_property
    def vtag(self) -> str:
        mat = G.PAT_SPEC_VTAG.match(self._spec)
        assert mat is not None, "Cannot parse %vtag from the spec"
        return mat[2]

    @cached_property
    def service(self):
        return f"""\
<services>
    <service name="obs_scm">
        <param name="scm">git</param>
        <param name="url">https://github.com/{G.GH_REPO}</param>
        <param name="revision">main</param>
        <param name="subdir">{self.name}</param>
        <param name="filename">source</param>
        <param name="versionformat">%h</param>
        <param name="extract">manifest {self.name}.changes {self.name}.spec</param>
    </service>
    <service name="extract_file" mode="buildtime">
        <param name="archive">_service:obs_scm:source-*.obscpio</param>
        <param name="files">source-*/*</param>
    </service>
    <service name="download_url" mode="buildtime">
        <param name="download-manifest">manifest</param>
    </service>
</services>\
"""

    def update(self, vtag: T.Optional[str] = None):
        """
        Updates this package.
        """
        vtag = vtag or self._fetch_newtag(self.vtag)
        if vtag is None:
            return
        L.info(f"Updating SPEC of <{self.name}>")
        new_version = self._parse_version(vtag)
        new_spec = self._spec
        new_spec = G.PAT_SPEC_VTAG.sub(rf"\1 {vtag}", new_spec)
        new_spec = G.PAT_SPEC_VERSION.sub(rf"\1 {new_version}", new_spec)
        new_spec = G.PAT_SPEC_AUTORELEASE.sub(r"\1", new_spec)
        write(self._spec_path, new_spec)
        L.info(f"Updating changelog of <{self.name}>")
        now = datetime.now().strftime("%c")
        changes = f"""\
* {now} {G.COMMIT_USERNAME} <{G.COMMIT_EMAIL}> - {new_version}-1
- Update to {vtag}

"""

        changes += read(self._changelog_path)
        write(self._changelog_path, changes)
        L.info(f"Updating manifest of <{self.name}>")
        write(self._manifest_path, "\n".join(self._sources(vtag)))
        return vtag

    def release(self, vtag: T.Optional[str] = None):
        """
        Release updates.
        """
        vtag = vtag or self.vtag
        git("add", self.name)
        git("commit", "-m", f"chore({self.name}): update to {vtag}")
        git("push", "--follow-tags")

    def update_service(self):
        """
        Updates services of this package.
        """
        L.info(f"Updating '_service' of <{self.name}>")
        obs_api(
            f"/source/{G.OBS_PROJECT}/{self.name}/_service",
            method="PUT",
            headers={"Content-Type": "application/xml"},
            params="Update _service",
            data=self.service,
        )

    def rebuild(self):
        """
        Trigger rebuild of this package.
        """
        L.info(f"Rebuilding <{self.name}>")
        obs_api(
            f"/trigger/runservice",
            method="POST",
            auth="token",
            params={"project": G.OBS_PROJECT, "package": self.name},
        )

    def _parse_version(self, vtag: str) -> str:
        """
        Parses %version from %vtag.
        """
        mat = G.PAT_VERSION.match(vtag)
        assert mat is not None
        return mat[1]

    def _fetch_newtag(self, vtag: str) -> T.Optional[str]:
        """
        Fetches the new %vtag if no avaiable `None` should be returned.
        """
        L.warning(f"<{self.name}> cannot be updated")
        return None

    def _sources(self, vtag: str) -> T.List[str]:
        """
        Returns remote sources used by this package.
        """
        L.warning(f"<{self.name}> doesn't provide any sources")
        return []


class GhPackage(Package):
    def __init__(self, name: str, repo: str):
        super().__init__(name)
        self.repo = repo

    def _fetch_newtag(self, vtag: str) -> T.Optional[str]:
        L.info(f"Fetching the latest release of {self.repo}")
        resp = gh_api(f"/repos/{self.repo}/releases/latest")
        latest_vtag = resp["tag_name"]
        if latest_vtag != vtag:
            return latest_vtag


class NixMount(Package):
    def __init__(self):
        super().__init__("nix-mount")

    def _sources(self, vtag: str) -> T.List[str]:
        return [f"nix.mount", f"nix-mount.service"]


class SarasaGothicFonts(GhPackage):
    def __init__(self):
        super().__init__("sarasa-gothic-fonts", "be5invis/Sarasa-Gothic")

    def _sources(self, vtag: str) -> T.List[str]:
        version = self._parse_version(vtag)
        return [
            f"https://github.com/{self.repo}/releases/download/{vtag}/sarasa-gothic-ttc-{version}.7z",
            f"https://raw.githubusercontent.com/{self.repo}/{vtag}/LICENSE",
            f"https://raw.githubusercontent.com/{self.repo}/{vtag}/README.md",
        ]


class SymbolsNerdFonts(GhPackage):
    def __init__(self):
        super().__init__("symbols-nerd-fonts", "ryanoasis/nerd-fonts")

    def _sources(self, vtag: str) -> T.List[str]:
        return [
            f"https://github.com/{self.repo}/releases/download/{vtag}/NerdFontsSymbolsOnly.zip",
            f"https://raw.githubusercontent.com/{self.repo}/{vtag}/LICENSE",
            f"https://raw.githubusercontent.com/{self.repo}/{vtag}/readme.md",
            f"https://raw.githubusercontent.com/{self.repo}/{vtag}/10-nerd-font-symbols.conf",
        ]


class Wezterm(GhPackage):
    def __init__(self):
        super().__init__("wezterm", "wez/wezterm")

    def _parse_version(self, vtag: str) -> T.Optional[str]:
        mat = G.PAT_WEZTERM_VERSION.match(vtag)
        assert mat is not None
        return mat[1]

    def _sources(self, vtag: str) -> T.List[str]:
        return [
            f"https://github.com/{self.repo}/releases/download/{vtag}/{self.name}-{vtag}-src.tar.gz"
        ]


class App:
    @cached_property
    def cli(self):
        parser = ArgumentParser()
        parser.add_argument("--update", action="store_true")
        parser.add_argument("--release", action="store_true")
        parser.add_argument("--show-service", action="store_true")
        parser.add_argument("--update-service", action="store_true")
        parser.add_argument("--rebuild", action="store_true")
        parser.add_argument("-o", "--outdir")
        package = parser.add_mutually_exclusive_group(required=True)
        package.add_argument("-a", "--all", action="store_true")
        package.add_argument("-p", "--package", action="append")
        return parser.parse_args()

    def run(self):
        args = self.cli
        if args.all:
            packages: T.List[Package] = [p() for p in G.PACKAGES.values()]
        else:
            packages = []
            for pname in args.package:
                package = G.PACKAGES.get(pname)
                assert package is not None, f"<{pname}> is not defined"
                packages.append(package())

        for package in packages:
            vtag = package.update() if args.update else package.vtag
            if args.release:
                package.release()
            if args.show_service:
                print(package.service)
            if args.update_service:
                package.update_service()
            if args.rebuild and vtag is not None:
                package.rebuild()


if __name__ == "__main__":
    L.basicConfig(
        level=L.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    App().run()
