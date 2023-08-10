from lib import BasePackage
import typing as T


class Package(BasePackage):
    def __init__(self):
        super().__init__("nix-mount")

    def _sources(self) -> T.List[str]:
        return ["nix.mount", "nix-mount.service"]
