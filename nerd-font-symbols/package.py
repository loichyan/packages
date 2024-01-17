from lib import FontPackage
import typing as T


class Package(FontPackage):
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
