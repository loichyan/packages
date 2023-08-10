from lib import GhPackage, cmd
import typing as T


class Package(GhPackage):
    def __init__(self):
        super().__init__("v2raya", "v2rayA/v2rayA")

    def _sources(self) -> T.List[str]:
        return [
            f"https://github.com/{self.repo}/archive/refs/tags/{self.vtag}.tar.gz#v2rayA-{self.version}",
        ]

    def _post_unpack(self):
        # Vendor dependencies for offline build
        cmd("go", "mod", "vendor", cwd="service")
