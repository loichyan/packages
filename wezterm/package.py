from datetime import datetime
from lib import G, GhPackage, Release
import typing as T


class Package(GhPackage):
    def __init__(self):
        super().__init__("wezterm", "wez/wezterm")

    def _parse_version(self, vtag: str) -> str:
        mat = G.PAT_NIGHTLY_VERSION.match(vtag)
        if mat is not None:
            return mat[1]

        mat = G.PAT_WEZTERM_VERSION.match(vtag)
        assert mat is not None
        return mat[1]

    def _fetch_latest(self) -> Release:
        nightly = G.PAT_NIGHTLY_VERSION.match(self.vtag)
        if nightly is not None:
            return Release(tag=self.vtag, date=datetime.strptime(nightly[1], "%Y%m%d"))

        return super()._fetch_latest()

    def _sources(self) -> T.List[str]:
        nightly = G.PAT_NIGHTLY_VERSION.match(self.vtag)
        if nightly is not None:
            return [f"git+https://github.com/{self.repo}.git?commit={nightly[2]}"]

        return [
            f"https://github.com/{self.repo}/releases/download/{self.vtag}/{self.name}-{self.vtag}-src.tar.gz"
        ]
