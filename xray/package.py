from lib import GhPackage, cmd
import typing as T


class Package(GhPackage):
    def __init__(self):
        super().__init__("xray", "XTLS/Xray-core")

    def _sources(self) -> T.List[str]:
        return [
            f"https://github.com/{self.repo}/archive/{self.vtag}.tar.gz",
        ]

    def _post_unpack(self):
        # Vendor dependencies for offline build
        cmd("go", "mod", "vendor")