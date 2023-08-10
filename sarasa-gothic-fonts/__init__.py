from lib import FontPackage
import typing as T


class Package(FontPackage):
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
