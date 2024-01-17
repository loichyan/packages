from lib import FontPackage
import typing as T


class Package(FontPackage):
    def __init__(self):
        super().__init__("rec-mono", "arrowtype/recursive")

    def _sources(self) -> T.List[str]:
        return [
            f"https://github.com/{self.repo}/releases/download/{self.vtag}/ArrowType-Recursive-{self.version}.zip",
            f"{self.fontname}.metainfo.xml",
        ]
