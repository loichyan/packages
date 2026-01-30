import typing as T
from lib import LocalPackage


class Package(LocalPackage):
    def __init__(self):
        super().__init__("nvidia-driver")

    def _sources(self) -> T.List[str]:
        return ["macros.kmodtool"]
