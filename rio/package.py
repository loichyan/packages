from lib import GhPackage
import typing as T


class Package(GhPackage):
    def __init__(self):
        super().__init__("rio", "raphamorim/rio")

    def _sources(self) -> T.List[str]:
        return [
            f"https://github.com/{self.repo}/archive/{self.vtag}.tar.gz",
        ]
