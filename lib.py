import git
import github
import hashlib
import itertools
import logging as L
import os
import re
import requests as R
import subprocess
import shutil as sh
import typing as T
from dataclasses import dataclass
from datetime import datetime
from functools import cached_property
from os.path import join, basename, exists
from subprocess import run
from tempfile import mkdtemp
from urllib.parse import urlparse
from xml.etree import ElementTree as ET


def cmd(
    *args: str,
    input: T.Optional[str] = None,
    cwd: T.Optional[str] = None,
    env: T.Optional[T.Dict[str, str]] = None,
):
    resp = run(
        args,
        input=input.encode() if input else None,
        stdout=subprocess.PIPE,
        cwd=cwd,
        env={**os.environ.copy(), **env} if env is not None else None,
    )
    resp.check_returncode()
    return resp.stdout.decode()


def download(url: str, outfile: str):
    L.info(f"Downloading {url} to {outfile}")
    return cmd("curl", "-fsSL", url, f"-o{outfile}")


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
        return require_env("GH_REPO", "loichyan/packages")

    @cached_property
    def GH_BRANCH(self):
        return require_env("GH_BRANCH", "main")

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
        repo = git.Repo()  # type: ignore
        with repo.config_writer() as w:
            w.set_value("user", "name", self.COMMIT_USERNAME)
            w.set_value("user", "email", self.COMMIT_EMAIL)
        return repo


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


@dataclass
class Release:
    tag: str
    date: datetime


class BasePackage:
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
        <param name="revision">{G.GH_BRANCH}</param>
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
    def date(self):
        return datetime.fromisoformat(self._spec.metadata["date"])

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
        release = self._fetch_latest()

        if release.date <= self.date:
            return
        vtag = release.tag
        version = self._parse_version(vtag)
        self._spec.save(
            vtag=vtag,
            date=release.date.isoformat(),
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
        outdir = outdir or mkdtemp()
        # Download sources
        srcdir = join(outdir, f"{self.name}-{self.version}")
        os.makedirs(srcdir, exist_ok=True)
        sources: T.List[str] = []
        for source in self._sources():
            url = urlparse(source)
            srcname = basename(url.path)
            srcfile = join(srcdir, url.fragment if url.fragment else srcname)
            sources.append(srcfile)
            if exists(srcfile):
                continue
            if url.scheme == "":
                sh.copy(join(self.name, url.path), srcfile)
            else:
                download(source, srcfile)
        # Trigger the prep hook
        workdir = mkdtemp()
        pwd = os.getcwd()
        prep_script = join(pwd, self.name, "prep")
        if exists(prep_script):
            os.chdir(workdir)
            try:
                env: T.Dict[str, str] = {}
                for i, v in enumerate(sources):
                    env[f"SOURCE{i}"] = v
                for k, v in itertools.chain(
                    self._spec.metadata.items(),
                    self._metadata().items(),
                ):
                    env[k] = v
                cmd(prep_script, env=env)
            finally:
                os.chdir(pwd)
        else:
            for s in sources:
                sh.copy(s, workdir)
        # Compress all sources
        outbase = f"{self.name}-{self.version}.src"
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
        G.REPO.git.add(self.name)
        lastcommit = G.REPO.index.commit(f"chore({self.name}): {msg}").hexsha
        repo = G.GH.get_repo(G.GH_REPO)
        release = repo.get_release("nightly")
        file_names = set(basename(f) for f in self._files)
        for asset in release.get_assets():
            fname = asset.name
            if fname in file_names:
                L.warning(f"Deleting existing asset {fname}")
                file_names.remove(fname)
                assert asset.delete_asset(), f"Cannot delete asset {fname}"
            if len(file_names) == 0:
                break
        for f in self._files:
            L.info(f"Uploading asset {f}")
            release.upload_asset(f, name=basename(f))
        L.info("Push commits")
        G.REPO.remote().push()
        L.info(f"Updating nightly tag ref to {lastcommit}")
        repo.get_git_ref("tags/nightly").edit(lastcommit)

    def rebuild(self):
        """
        Trigger rebuild of this package.
        """
        L.info(f"Rebuilding {self.name}")
        G.OBS.trigger(self.name)

    def _fetch_latest(self) -> Release:
        """
        Fetches the latest %vtag.
        """
        return Release(tag=self.vtag, date=self.date)

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


class LocalPackage(BasePackage):
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


class GhPackage(BasePackage):
    def __init__(self, name: str, repo: str):
        super().__init__(name)
        self.repo = repo

    @cached_property
    def _gh_repo(self):
        return G.GH.get_repo(self.repo)

    def _fetch_latest(self) -> Release:
        L.info(f"Fetching the latest release of {self.repo}")
        release = self._gh_repo.get_latest_release()
        return Release(tag=release.tag_name, date=release.created_at)


class FontPackage(GhPackage):
    def __init__(self, fontname: str, repo: str, name: T.Optional[str] = None):
        name = name or f"{fontname}-fonts"
        super().__init__(name, repo)
        self.fontname = fontname

    def _metadata(self) -> T.Dict[str, str]:
        return dict(fontname=self.fontname, **super()._metadata())
