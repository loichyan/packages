#!/usr/bin/env python3

from argparse import ArgumentParser
from datetime import datetime
from functools import cached_property
from os.path import join, basename
from subprocess import run
from tempfile import mkdtemp
from urllib.parse import urlparse
from xml.etree import ElementTree as ET
import git
import github
import hashlib
import logging as L
import os
import re
import requests as R
import subprocess
import shutil as sh
import typing as T


def cmd(*args: str, input: T.Optional[str] = None):
    resp = run(
        args,
        input=input.encode() if input else None,
        stdout=subprocess.PIPE,
    )
    resp.check_returncode()
    return resp.stdout.decode()


def download(url: str, outfile: str):
    L.info(f"Downloading {url} to {outfile}")
    return cmd("wget", url, f"-O{outfile}")


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
    def OBS(self):
        return Obs()

    @cached_property
    def OBS_HOST(self):
        return require_env("OBS_HOST", "api.opensuse.org")

    @cached_property
    def GH(self):
        return github.Github(auth=github.Auth.Token(require_env("GH_TOKEN")))

    @cached_property
    def GH_REPO(self):
        return self.GH.get_repo(require_env("GH_REPO", "loichyan/packages"))

    @cached_property
    def COMMIT_USERNAME(self):
        return require_env("COMMIT_USERNAME", "github-actions[bot]")

    @cached_property
    def COMMIT_EMAIL(self):
        return require_env(
            "COMMIT_EMAIL",
            "github-actions[bot]@users.noreply.github.com",
        )

    @cached_property
    def REPO(self):
        repo = git.Repo()
        with repo.config_writer() as w:
            w.set_value("user", "name", self.COMMIT_USERNAME)
            w.set_value("user", "email", self.COMMIT_EMAIL)
        return repo

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


class Obs:
    def _api(
        self,
        method: str,
        path: str,
        params: T.Optional[T.Dict[str, str]] = None,
        auth: T.Optional[str] = None,
        headers: T.Optional[T.Dict[str, str]] = None,
        data: T.Optional[str] = None,
    ) -> ET.Element:
        """
        Calls OBS API.
        """
        auth = auth or f"Basic {G.OBS_LOGIN}"
        headers = headers or {}
        L.info(f"Calling OBS API: {path}")
        resp = R.request(
            method,
            f"https://{G.OBS_HOST}{path}",
            params=params,
            headers={
                "Accept": "application/xml; charset=utf-8",
                "Authorization": auth,
                **headers,
            },
            data=data,
        )
        tree = ET.fromstring(resp.text)
        if resp.status_code != 200:
            summary = tree.find("./status/summary")
            summary = summary.text if summary is not None else None
            raise RuntimeError(f"OBS API error: {summary or resp.text}")
        return tree

    def trigger(self, package: str, cmd: T.Optional[str] = None):
        cmd = cmd or "runservice"
        self._api(
            "POST",
            f"/trigger/{cmd}",
            params={"project": G.OBS_PROJECT, "package": package},
            auth=f"Token {G.OBS_TOKEN}",
        )

    def update_service(self, package: str, service: str, msg: T.Optional[str]):
        msg = msg or "Update `_service`"
        self._api(
            "PUT",
            f"/source/{G.OBS_PROJECT}/{package}/_service",
            params={"comment": msg},
            headers={"Content-Type": "application/xml"},
            data=service,
        )


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
        <param name="filename">{self.name}-git</param>
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

    def update_service(self, msg: T.Optional[str] = None):
        """
        Updates services of this package.
        """
        L.info(f"Updating '_service' of {self.name}")
        G.OBS.update_service(self.name, self.service, msg)

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
                sh.copy(
                    cachefile,
                    join(workdir, url.fragment if url.fragment else filename),
                )
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
            checksum=f"sha256:{checksum}",
        )
        self._files.extend((outfile, outchecksum))
        return outdir

    def release(self, msg: T.Optional[str] = None):
        """
        Releases updates.
        """
        msg = msg or f"update to {self.version}"
        L.info(f"Commiting changes")
        G.REPO.index.add([self.name])
        lastcommit = G.REPO.index.commit(f"chore({self.name}): {msg}").hexsha
        release = G.GH_REPO.get_release("nightly")
        L.info("Push commits")
        G.REPO.remote().push()
        L.info(f"Updating nightly tag ref to {lastcommit}")
        G.GH_REPO.get_git_ref("tags/nightly").edit(lastcommit)
        for f in self._files:
            L.info(f"Uploading asset {f}")
            release.upload_asset(f)

    def rebuild(self):
        """
        Trigger rebuild of this package.
        """
        L.info(f"Rebuilding {self.name}")
        G.OBS.trigger(self.name)

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
        will be unpacked and stripped with the optional '#<subdir>' fragment. Other files can be renamed
        with the optional '#<newname>' fragment.
        """
        return []

    def _post_unpack(self):
        """
        Runs after all downloaded sources are unpacked.
        """
        ...


class LocalPackage(Package):
    def update_service(self, msg: T.Optional[str] = None):
        return

    def update(self):
        return None

    def update_source(self, outdir: T.Optional[str] = None):
        return outdir or mkdtemp()

    def release(self, msg: T.Optional[str] = None):
        return

    def rebuild(self):
        return


class GhPackage(Package):
    def __init__(self, name: str, repo: str):
        super().__init__(name)
        self.repo = repo

    @cached_property
    def _gh_repo(self):
        return G.GH.get_repo(self.repo)

    def _fetch_latest(self) -> str:
        L.info(f"Fetching the latest release of {self.repo}")
        return self._gh_repo.get_latest_release().tag_name


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
            f"https://raw.githubusercontent.com/{self.repo}/{self.vtag}/readme.md#README.md",
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
            packages: T.List[Package] = [p() for p in G.PACKAGES.values()]
        else:
            packages = []
            for pname in args.package:
                package = G.PACKAGES.get(pname)
                assert package is not None, f"{pname} is not defined"
                packages.append(package())

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
    sh.register_unpack_format(
        "7zip",
        ["7z"],
        lambda src, dst: cmd("7z", "x", src, f"-o{dst}"),
    )
    App().run()
