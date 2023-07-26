#!/usr/bin/env python3

from argparse import ArgumentParser
from datetime import datetime
from functools import cached_property
from os.path import join, basename
from subprocess import run
from tempfile import mkdtemp
from urllib.parse import urlparse
from xml.etree import ElementTree as ET
import hashlib
import io
import json
import logging as L
import os
import re
import requests as R
import subprocess
import shutil as sh
import typing as T


def cmd(*args: str, stdin: T.Optional[T.IO[T.Any]] = None):
    resp = run(
        args,
        stdin=stdin,
        stdout=subprocess.PIPE,
    )
    resp.check_returncode()
    return resp.stdout.decode()


def gh(*args: str, stdin: T.Optional[T.IO[T.Any]] = None):
    return cmd("gh", *args, stdin=stdin)


def download(url: str, outfile: str):
    L.info(f"Downloading {url} to {outfile}")
    return cmd("wget", url, f"-O{outfile}")


def git(*args: str):
    return cmd(
        "git",
        "-c",
        f"user.name={G.COMMIT_USERNAME}",
        "-c",
        f"user.email={G.COMMIT_EMAIL}",
        *args,
    )


def obs_api(
    path: str,
    method: T.Optional[str] = None,
    auth: T.Optional[T.Literal["login", "token"]] = None,
    headers: T.Optional[T.Dict[str, str]] = None,
    **kwargs: T.Any,
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
    resp = R.request(
        method or "GET",
        f"https://{G.OBS_HOST}{path}",
        headers={
            "Accept": "application/xml; charset=utf-8",
            "Authorization": authorization,
            **(headers or {}),
        },
        **kwargs,
    )
    tree = ET.fromstring(resp.text)
    if resp.status_code != 200:
        summary = tree.find("./status/summary")
        summary = summary.text if summary is not None else None
        raise RuntimeError(f"OBS API error: {summary or resp.text}")
    return tree


def gh_api(
    path: str,
    method: T.Optional[str] = None,
    body: T.Optional[T.Any] = None,
) -> T.Any:
    L.info(f"Calling GitHub API {path}")
    out = gh(
        "api",
        path,
        "-X",
        method or "GET",
        "-H",
        "Content-Type: application/json",
        stdin=io.StringIO(json.dumps(body)) if body is not None else None,
    )
    return json.loads(out)


def sha256(path: str) -> str:
    hash = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()


def write(path: str, content: str):
    with open(path, "w") as f:
        f.write(content)


def read(path: str):
    with open(path, "r") as f:
        return f.read()


def ls(path: str = "."):
    for f in os.listdir(path):
        yield join(path, f)


def require_env(key: str, default: T.Optional[str] = None) -> str:
    val = os.environ.get(key) or default
    assert val is not None, f"${key} must be specified"
    return val


class Global:
    @cached_property
    def PAT_METADATA(self):
        return re.compile(r"^%define (\w+) (.+)$")

    @cached_property
    def PAT_VERSION(self):
        return re.compile(r"^v(.+)$")

    @cached_property
    def PAT_WEZTERM_VERSION(self):
        return re.compile(r"^(\d+)-(\d+)-([0-9a-f]+)$")

    @cached_property
    def ARCHIVE_TYPES_AND_EXTS(self):
        all: T.List[T.Tuple[str, str]] = []
        for ty, exts, _ in sh.get_unpack_formats():
            all.extend((ty, e) for e in exts)
        return all

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
            "akmods-keys": AkmodsKeys,
            "nerd-font-symbols": NerdFontSymbols,
            "nix-mount": NixMount,
            "sarasa-gothic-fonts": SarasaGothicFonts,
            "wezterm": Wezterm,
        }


G = Global()


class Spec:
    def __init__(self, path: str):
        content: T.List[str] = []
        metadata: T.Dict[str, str] = {}
        with open(path) as f:
            for line in f:
                mat = G.PAT_METADATA.match(line)
                if mat is not None:
                    metadata[mat[1]] = mat[2]
                else:
                    content.append(line)
                    break
            for line in f:
                content.append(line)
        self.path = path
        self.content = content
        self.metadata = metadata

    def save(self, **metadata: str):
        L.info(f"Updating SPEC file {self.path}")
        self.metadata.update(metadata)
        with open(self.path, "w") as f:
            for k, v in self.metadata.items():
                f.write(f"%define {k} {v}\n")
            for content in self.content:
                f.write(content)


class Package:
    def __init__(self, name: str):
        self.name = name
        self._files: T.List[str] = []

    @cached_property
    def _changelog_path(self):
        return join(self.name, f"{self.name}.changes")

    @cached_property
    def _spec(self):
        return Spec(join(self.name, f"{self.name}.spec"))

    @cached_property
    def service(self):
        return f"""\
<services>
    <service name="obs_scm">
        <param name="scm">git</param>
        <param name="url">https://github.com/{G.GH_REPO}</param>
        <param name="revision">main</param>
        <param name="subdir">{self.name}</param>
        <param name="filename">{self.name}-manifest</param>
        <param name="versionformat">%h</param>
        <param name="extract">*.spec</param>
        <param name="extract">*.changes</param>
    </service>
    <service name="download_assets"></service>
</services>\
"""

    @property
    def vtag(self):
        return self._spec.metadata["vtag"]

    @property
    def version(self):
        return self._spec.metadata["version"]

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

    def update(self) -> T.Optional[str]:
        """
        Updates this package, returns the new %vtag if avialable.
        """
        vtag = self._fetch_latest()
        if vtag == self.vtag:
            return
        version = self._parse_version(vtag)
        self._spec.save(
            vtag=vtag,
            version=version,
            release="%autorelease",
            **self._metadata(),
        )
        L.info(f"Updating changelog of {self.name}")
        now = datetime.now().strftime("%c")
        changes = f"""\
* {now} {G.COMMIT_USERNAME} <{G.COMMIT_EMAIL}> - {version}-1
- Update to {version}

"""
        changes += read(self._changelog_path)
        write(self._changelog_path, changes)
        return vtag

    def update_source(self, outdir: T.Optional[str] = None):
        """
        Downloads and compresses all needed sources.
        """
        cachedir = join(".cache", f"{self.name}-{self.version}")
        os.makedirs(cachedir, exist_ok=True)
        outdir = outdir or mkdtemp()
        # Download sources
        workdir = mkdtemp()
        for source in self._sources():
            url = urlparse(source)
            source = source[: len(source) - len(url.fragment)]
            filename = basename(url.path)
            if url.scheme == "":
                cachefile = join(self.name, url.path)
            else:
                cachefile = join(cachedir, filename)
                if not os.path.exists(cachefile):
                    download(source, cachefile)
            for ty, ext in G.ARCHIVE_TYPES_AND_EXTS:
                # Unpack all files to the outdir if supported
                if filename.endswith(ext):
                    tmpdir = mkdtemp()
                    L.info(f"Unpacking {cachefile} to {tmpdir}")
                    sh.unpack_archive(cachefile, tmpdir, ty)
                    for f in ls(join(tmpdir, url.fragment)):
                        sh.move(f, workdir)
                    sh.rmtree(tmpdir)
                    break
            else:
                # or copy it to the outdir
                sh.copy(cachefile, join(workdir, filename))
        # Trigger the post-unpack hook
        cwd = os.getcwd()
        try:
            os.chdir(workdir)
            self._post_unpack()
        finally:
            os.chdir(cwd)
        # Compress all sources
        outbase = f"{self.name}-{self.version}-source"
        outext = "tar.xz"
        outfile = join(outdir, f"{outbase}.{outext}")
        L.info(f"Compressing {workdir} to {outfile}")
        sh.make_archive(join(outdir, outbase), "xztar", workdir)
        sh.rmtree(workdir)
        L.info(f"Calculates checksum of {outfile}")
        checksum = sha256(outfile)
        outchecksum = join(outdir, f"{outbase}.sha256")
        write(outchecksum, checksum)
        self._spec.save(
            source=f"https://github.com/{G.GH_REPO}/releases/download/nightly/{outbase}.{outext}",
            checksum=checksum,
        )
        self._files.extend((outfile, outchecksum))
        return outdir

    def upload(self):
        """
        Uploads attached files.
        """
        L.info("Uploading %s" % (",".join(self._files)))
        gh("release", "upload", "nightly", *self._files)

    def commit(self):
        """
        Releases updates.
        """
        git("add", self.name)
        git("commit", "-m", f"chore({self.name}): update to {self.version}")
        git("push")
        lastcommit = git("rev-parse", "HEAD")
        L.info(f"Updating nightly tag ref to {lastcommit}")
        gh_api(
            f"/repos/{G.GH_REPO}/git/refs/nightly",
            method="PATCH",
            body={"sha": lastcommit},
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

    def _metadata(self) -> T.Dict[str, str]:
        """
        Returns additional metadata which is inserted to the SPEC file.
        """
        return {}

    def _sources(self) -> T.List[str]:
        """
        Returns sources use by this package, supports local and remote URLs. All supported arvhices
        will be unpacked and stripped with the optional '#<subdir>' fragment.
        """
        return []

    def _post_unpack(self):
        """
        Runs after all downloaded sources are unpacked.
        """
        ...


class LocalPackage(Package):
    def update_service(self):
        return

    def update(self):
        return None

    def update_source(self, outdir: T.Optional[str] = None):
        return outdir or mkdtemp()

    def commit(self):
        return

    def upload(self):
        return

    def rebuild(self):
        return


class GhPackage(Package):
    def __init__(self, name: str, repo: str):
        super().__init__(name)
        self.repo = repo

    def _fetch_latest(self) -> str:
        L.info(f"Fetching the latest release of {self.repo}")
        resp = gh_api(f"/repos/{self.repo}/releases/latest")
        return resp["tag_name"]


class FontPackage(GhPackage):
    def __init__(self, fontname: str, repo: str, name: T.Optional[str] = None):
        name = name or f"{fontname}-fonts"
        super().__init__(name, repo)
        self.fontname = fontname

    def _metadata(self) -> T.Dict[str, str]:
        return {"fontname": self.fontname}


class AkmodsKeys(LocalPackage):
    def __init__(self):
        super().__init__("akmods-keys")


class NerdFontSymbols(FontPackage):
    def __init__(self):
        super().__init__(
            "nerd-font-symbols",
            "ryanoasis/nerd-fonts",
            "nerd-font-symbols",
        )

    def _sources(self) -> T.List[str]:
        return [
            f"https://github.com/{self.repo}/releases/download/{self.vtag}/NerdFontsSymbolsOnly.zip",
            f"https://raw.githubusercontent.com/{self.repo}/{self.vtag}/LICENSE",
            f"https://raw.githubusercontent.com/{self.repo}/{self.vtag}/readme.md",
            f"https://raw.githubusercontent.com/{self.repo}/{self.vtag}/10-{self.fontname}.conf",
            f"{self.fontname}.metainfo.xml",
        ]

    def _post_unpack(self):
        # Remove windows compatible fonts
        for f in ls():
            if f.endswith("Windows Compatible.ttf"):
                os.remove(f)


class NixMount(Package):
    def __init__(self):
        super().__init__("nix-mount")

    def _sources(self) -> T.List[str]:
        return ["nix.mount", "nix-mount.service"]


class SarasaGothicFonts(FontPackage):
    def __init__(self):
        super().__init__("sarasa-gothic", "be5invis/Sarasa-Gothic")

    def _metadata(self) -> T.Dict[str, str]:
        return {"fontname": self.fontname}

    def _sources(self) -> T.List[str]:
        return [
            f"https://github.com/{self.repo}/releases/download/{self.vtag}/{self.fontname}-ttc-{self.version}.7z",
            f"https://raw.githubusercontent.com/{self.repo}/{self.vtag}/LICENSE",
            f"https://raw.githubusercontent.com/{self.repo}/{self.vtag}/README.md",
            f"{self.fontname}.metainfo.xml",
        ]


class Wezterm(GhPackage):
    def __init__(self):
        super().__init__("wezterm", "wez/wezterm")

    def _parse_version(self, vtag: str) -> str:
        mat = G.PAT_WEZTERM_VERSION.match(vtag)
        assert mat is not None
        return mat[1]

    def _sources(self) -> T.List[str]:
        return [
            f"https://github.com/{self.repo}/releases/download/{self.vtag}/{self.name}-{self.vtag}-src.tar.gz#{self.name}-{self.vtag}"
        ]

    def _post_unpack(self):
        # Vendor dependencies for offline build
        config = cmd("cargo", "vendor")
        with open(join(".cargo", "config"), "a") as f:
            f.write(config)


class App:
    @cached_property
    def cli(self):
        parser = ArgumentParser()
        parser.add_argument("--show-service", action="store_true")
        parser.add_argument("--update-service", action="store_true")
        parser.add_argument("--update", action="store_true")
        parser.add_argument("--update-source", action="store_true")
        parser.add_argument("--upload", action="store_true")
        parser.add_argument("--commit", action="store_true")
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
            if args.show_service:
                print(package.service)
            if args.update_service:
                package.update_service()
            updated = args.update and package.update() is not None
            if updated or not args.update:
                if args.update_source:
                    package.update_source(args.outdir)
                if args.upload:
                    package.upload()
                if args.commit:
                    package.commit()
                if args.rebuild:
                    package.rebuild()


if __name__ == "__main__":
    L.basicConfig(
        level=L.INFO,
        format="[%(asctime)s] [%(levelname)s] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    sh.register_unpack_format(
        "7zip",
        ["7z"],
        lambda src, dst: cmd("7z", "x", src, f"-o{dst}"),
    )
    App().run()
