#!/usr/bin/env python3

from argparse import ArgumentParser
from datetime import datetime
from enum import IntEnum
from functools import cached_property
from subprocess import run
from tempfile import mkdtemp
from textwrap import dedent
from urllib.parse import urlparse
from xml.etree import ElementTree as ET
import hashlib
import logging as L
import os
import re
import requests as R
import shutil as sh
import typing as T


def un7zip(src: str, dest: str, **kwargs):
    run(["7z", "x", src, f"-o{dest}"])


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


def gh(*args: str):
    run(["gh", *args])


def sha256(path: str):
    hash = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()


def write(path: str, content: str):
    with open(path, "w") as f:
        f.write(content)


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
    def GH_REPO(self):
        return require_env("GH_REPO", "loichyan/packages")

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
        return require_env("COMMIT_USERNAME", "github-actions")

    @cached_property
    def COMMIT_EMAIL(self):
        return require_env("COMMIT_EMAIL", "github-actions@github.com")

    @cached_property
    def GITHUB_OUTPUT(self):
        return require_env("GITHUB_OUTPUT")

    @cached_property
    def PACKAGES(self) -> T.Dict[str, T.Callable[[], "Package"]]:
        return {
            "nix-mount": NixMount,
            "sarasa-gothic-fonts": SarasaGothicFonts,
            "symbols-nerd-fonts": SymbolsNerdFonts,
            "wezterm": Wezterm,
        }

    @cached_property
    def ARVHICE_EXTS(self):
        all: T.List[str] = []
        for _, exts, _ in sh.get_unpack_formats():
            all.extend(exts)
        return all


G = Global()


class Package:
    class Target(IntEnum):
        ARVHICE = 1
        COMMIT = 2
        RELEASE = 3

        def __str__(self) -> str:
            return self.name

    def __init__(self, name: str):
        self.name = name

    @cached_property
    def _spec_path(self):
        return f"{self.name}/{self.name}.spec"

    @cached_property
    def _changelog_path(self):
        return f"{self.name}/{self.name}.changes"

    @cached_property
    def _spec(self):
        with open(self._spec_path) as f:
            return f.read()

    @cached_property
    def vtag(self) -> str:
        mat = G.PAT_SPEC_VTAG.match(self._spec)
        assert mat is not None, "Cannot parse %vtag from the spec"
        return mat[2]

    def update_service(self):
        """
        Updates services of this package.
        """
        service = dedent(
            f"""\
            <services>
                <service name="obs_scm">
                    <param name="scm">git</param>
                    <param name="url">https://github.com/{G.GH_REPO}</param>
                    <param name="revision">main</param>
                    <param name="subdir">{self.name}</param>
                    <param name="filename">source</param>
                    <param name="without-version">true</param>
                </service>
                <service name="extract_file">
                    <param name="archive">_service:obs_scm:source.obscpio</param>
                    <param name="files">sources {self.name}.changes {self.name}.spec</param>
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
                - Bump version tag to {vtag}\n
                """
            )
            f.write(changes + changelog)
        return vtag

    def update_source(
        self,
        vtag: T.Optional[str] = None,
        outdir: T.Optional[str] = None,
    ):
        """
        Update sources and pack them into an gztar arvhice.
        """
        vtag = vtag or self.vtag
        outdir = outdir or mkdtemp()
        # Fetch all sources.
        workdir = mkdtemp()
        for source in self._sources(vtag):
            url = urlparse(source)
            filename = (
                url.fragment if url.fragment != "" else os.path.basename(url.path)
            )
            # Strip the fragment for correct copy path.
            outfile = f"{workdir}/{filename}"
            if url.scheme != "":
                L.info(f"Downloading {source}")
                run(["wget", f"-O{outfile}", source])
            else:
                sh.copyfile(f"{self.name}/{url.path}", outfile)
            # Unpack it if supported
            for ext in G.ARVHICE_EXTS:
                if filename.endswith(ext):
                    unpacked = filename[: -len(ext)]
                    sh.unpack_archive(outfile, f"{workdir}/{unpacked}")
                    os.remove(outfile)
                    break
        arc = f"{outdir}/{self.name}-{vtag}-source"
        L.info(f"Compressing {workdir}")
        sh.make_archive(arc, "gztar", workdir)
        checksum = sha256(f"{arc}.tar.gz")
        write(f"{outdir}/{self.name}-{vtag}-source.sha256", checksum)
        # Update the 'sources' file.
        write(
            f"{self.name}/sources",
            f"sha256 https://github.com/{G.GH_REPO}/releases/download/{vtag}/{arc}.tar.gz = {checksum}",
        )
        return outdir

    def release(
        self,
        vtag: T.Optional[str] = None,
        files: T.Optional[T.List[str]] = None,
    ):
        """
        Release the updates of this package.
        """
        vtag = vtag or self.vtag
        files = files or []
        L.info(f"Releasing <{self.name}>")
        tag = f"{self.name}-{vtag}"
        git("commit", "-m", f"chore({self.name}): update to {vtag}")
        git("tag", tag, "HEAD")
        git("push", "--follow-tags")
        gh("release", "create", "-n", f"Update `{self.name}` to {vtag}", tag, *files)

    def rebuild(self):
        """
        Trigger rebuild of this package.
        """
        L.info(f"Rebuilding <{self.name}>")
        self._obs_api(
            f"trigger/runservice",
            method="POST",
            auth="token",
            params={"project": G.OBS_PROJECT, "package": self.name},
        )

    def _obs_api(
        self,
        path: str,
        method: T.Optional[str] = None,
        auth: T.Optional[T.Literal["login", "token"]] = None,
        **kwargs,
    ) -> ET.Element:
        """
        Calls OBS API.
        """
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
        Returns sources used by this package. Arvhices will be uncompressed into a folder with the
        same name. A source can be renamed with the `#newname` suffix.

        Supported source types:

        1. Local files
        2. Remote files starts with `http://` or `https://`

        Supported arvhice types are `zip`, `tar`, `gztar`, `bztar`, `xztar`, or `7zip`.
        """
        L.warning(f"<{self.name}> doesn't provide any sources")
        return []


class GhPackage(Package):
    def __init__(self, name: str, repo: str):
        super().__init__(name)
        self.repo = repo

    def _fetch_newtag(self, vtag: str) -> T.Optional[str]:
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
            f"https://github.com/{self.repo}/releases/download/{vtag}/sarasa-gothic-ttc-{version}.7z#fonts.7z",
            f"https://raw.githubusercontent.com/{self.repo}/{vtag}/LICENSE",
            f"https://raw.githubusercontent.com/{self.repo}/{vtag}/README.md",
            f"{self.name}.metainfo.xml",
        ]


class SymbolsNerdFonts(GhPackage):
    def __init__(self):
        super().__init__("symbols-nerd-fonts", "ryanoasis/nerd-fonts")

    def _sources(self, vtag: str) -> T.List[str]:
        return [
            f"https://github.com/{self.repo}/releases/download/{vtag}/NerdFontsSymbolsOnly.zip#fonts.zip",
            f"https://raw.githubusercontent.com/{self.repo}/{vtag}/10-nerd-font-symbols.conf",
            f"https://raw.githubusercontent.com/{self.repo}/{vtag}/LICENSE",
            f"https://raw.githubusercontent.com/{self.repo}/{vtag}/readme.md#README.md",
            f"{self.name}.metainfo.xml",
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
            f"https://github.com/{self.repo}/releases/download/{vtag}/{self.name}-{vtag}-src.tar.gz#source.tar.gz"
        ]


class App:
    @cached_property
    def cli(self):
        parser = ArgumentParser()
        parser.add_argument("--update-service", action="store_true")
        parser.add_argument("--update", action="store_true")
        parser.add_argument("--update-source", action="store_true")
        parser.add_argument("--release", action="store_true")
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
            if args.update:
                vtag = package.update()
            else:
                vtag = None
            if args.update_source:
                source = package.update_source(vtag, args.outdir)
            else:
                source = None
            if args.release:
                files = os.listdir(source) if source is not None else None
                package.release(vtag, files)
            if args.update_service:
                package.update_service()
            if args.rebuild:
                package.rebuild()


if __name__ == "__main__":
    L.basicConfig(
        level=L.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    sh.register_unpack_format("7zip", ["7z"], un7zip)
    App().run()
