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
    if auth == None or auth == "login":
        authorization = f"Basic {G.OBS_LOGIN}"
    elif auth == "token":
        authorization = f"Token {G.OBS_TOKEN}"
    else:
        raise ValueError(f"Unsupported authorization method: '{auth}'")
    L.info(f"Calling OBS API: {path}")
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
    L.info(f"Calling GitHub API: {path}")
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
    @property
    def METADATA_BEGIN(self):
        return "# {{ METADATA BEGIN\n"

    @property
    def METADATA_END(self):
        return "# METADATA END }}\n"

    @cached_property
    def PAT_METADATA(self):
        return re.compile(r"^(?:%define (\w+)) (.+)$", flags=re.M)

    @cached_property
    def PAT_AUTORELEASE(self):
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
            "nerd-font-symbols": NerdFontSymbols,
            "nix-mount": NixMount,
            "sarasa-gothic-fonts": SarasaGothicFonts,
            "wezterm": Wezterm,
        }


G = Global()


class Spec:
    def __init__(self, path: str):
        metadata: T.Dict[str, str] = {}
        body = ""
        # 0 => Init
        # 1 => ParseMetadata
        state = 0
        with open(path) as f:
            for line in f:
                if state == 0:
                    if line == G.METADATA_BEGIN:
                        state = 1
                    else:
                        body += line
                elif state == 1:
                    if line == G.METADATA_END:
                        state = 0
                    else:
                        mat = G.PAT_METADATA.match(line)
                        assert mat is not None, f"Cannot parse metadata from {path}"
                        metadata[mat[1]] = mat[2]
        self.path = path
        self.metadata = metadata
        self.body = body

    def save(self):
        with open(self.path, "w") as f:
            f.write(G.METADATA_BEGIN)
            for k, v in self.metadata.items():
                f.write(f"%define {k} {v}\n")
            f.write(G.METADATA_END)
            f.write(self.body)


class Package:
    def __init__(self, name: str):
        self.name = name

    @cached_property
    def _changelog_path(self):
        return f"{self.name}/{self.name}.changes"

    @cached_property
    def _manifest_path(self):
        return f"{self.name}/manifest"

    @cached_property
    def _spec(self):
        return Spec(f"{self.name}/{self.name}.spec")

    @cached_property
    def service(self):
        return f"""\
<services>
    <service name="obs_scm">
        <param name="scm">git</param>
        <param name="url">https://github.com/{G.GH_REPO}</param>
        <param name="revision">main</param>
        <param name="subdir">{self.name}</param>
        <param name="filename">{self.name}-source</param>
        <param name="versionformat">%h</param>
        <param name="extract">{self.name}.changes</param>
        <param name="extract">{self.name}.spec</param>
    </service>
    <service name="extract_file" mode="buildtime">
        <param name="archive">_service:obs_scm:{self.name}-source-*.obscpio</param>
        <param name="files">{self.name}-source-*/*</param>
    </service>
    <service name="download_assets" mode="buildtime"></service>
</services>\
"""

    @property
    def vtag(self) -> str:
        return self._spec.metadata["vtag"]

    @property
    def version(self) -> str:
        return self._spec.metadata["version"]

    def update(self):
        """
        Updates this package.
        """
        vtag = self._fetch_latest()
        if vtag == self.vtag:
            return
        L.info(f"Updating SPEC of {self.name}")
        version = self._parse_version(vtag)
        spec = self._spec
        spec.metadata.update(
            self._metadata(), name=self.name, vtag=vtag, version=version
        )
        spec.body = G.PAT_AUTORELEASE.sub(r"\1", spec.body)
        spec.save()
        L.info(f"Updating changelog of {self.name}")
        now = datetime.now().strftime("%c")
        changes = f"""\
* {now} {G.COMMIT_USERNAME} <{G.COMMIT_EMAIL}> - {version}-1
- Update to {vtag}

"""
        changes += read(self._changelog_path)
        write(self._changelog_path, changes)
        return vtag

    def release(self):
        """
        Release updates.
        """
        vtag = self.vtag
        git("add", self.name)
        git("commit", "-m", f"chore({self.name}): update to {vtag}")
        git("push", "--follow-tags")

    def update_service(self):
        """
        Updates services of this package.
        """
        L.info(f"Updating '_service' of {self.name}")
        obs_api(
            f"/source/{G.OBS_PROJECT}/{self.name}/_service",
            method="PUT",
            headers={"Content-Type": "application/xml"},
            params={"comment": "Update `_service`"},
            data=self.service,
        )

    def rebuild(self):
        """
        Trigger rebuild of this package.
        """
        L.info(f"Rebuilding {self.name}")
        obs_api(
            f"/trigger/runservice",
            method="POST",
            auth="token",
            params={"project": G.OBS_PROJECT, "package": self.name},
        )

    def _metadata(self) -> T.Dict[str, str]:
        """
        Extra metadata prepended to the SPEC file.
        """
        return {}

    def _fetch_latest(self) -> str:
        """
        Fetches the latest %vtag.
        """
        L.warning(f"{self.name} cannot be updated")
        return self.vtag

    def _parse_version(self, vtag: str) -> str:
        """
        Parses %version from %vtag.
        """
        mat = G.PAT_VERSION.match(vtag)
        assert mat is not None
        return mat[1]


class LocalPackage(Package):
    def update(self):
        return


class GhPackage(Package):
    def __init__(self, name: str, repo: str):
        super().__init__(name)
        self.repo = repo

    def _metadata(self) -> T.Dict[str, str]:
        return {"repo": self.repo}

    def _fetch_latest(self) -> T.Optional[str]:
        L.info(f"Fetching the latest release of {self.repo}")
        resp = gh_api(f"/repos/{self.repo}/releases/latest")
        return resp["tag_name"]


class NixMount(Package):
    def __init__(self):
        super().__init__("nix-mount")


class SarasaGothicFonts(GhPackage):
    def __init__(self):
        super().__init__("sarasa-gothic-fonts", "be5invis/Sarasa-Gothic")


class NerdFontSymbols(GhPackage):
    def __init__(self):
        super().__init__("nerd-font-symbols-fonts", "ryanoasis/nerd-fonts")


class Wezterm(GhPackage):
    def __init__(self):
        super().__init__("wezterm", "wez/wezterm")

    def _parse_version(self, vtag: str) -> T.Optional[str]:
        mat = G.PAT_WEZTERM_VERSION.match(vtag)
        assert mat is not None
        return mat[1]


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
                assert package is not None, f"{pname} is not defined"
                packages.append(package())

        for package in packages:
            updated = args.update and package.update()
            if args.release:
                package.release()
            if args.show_service:
                print(package.service)
            if args.update_service:
                package.update_service()
            if args.rebuild and (updated or not args.update):
                package.rebuild()


if __name__ == "__main__":
    L.basicConfig(
        level=L.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    App().run()
