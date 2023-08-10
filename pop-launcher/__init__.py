from lib import GhPackage, cmd
import typing as T


class Package(GhPackage):
    def __init__(self):
        super().__init__("pop-launcher", "pop-os/launcher")

    def _parse_version(self, vtag: str) -> str:
        return vtag

    def _sources(self) -> T.List[str]:
        return [
            f"https://github.com/{self.repo}/archive/refs/tags/{self.vtag}.tar.gz#launcher-{self.version}",
        ]

    def _post_unpack(self):
        # Vendor dependencies for offline build
        cmd("just", "vendor")
