from lib import GhPackage, cmd
import typing as T


class Package(GhPackage):
    def __init__(self):
        super().__init__("librime", "rime/librime")
        self.lub_plugin_rev = "399b680793e4c0adf3a18422b7e3d452018aea06"

    def _parse_version(self, vtag: str) -> str:
        return vtag

    def _sources(self) -> T.List[str]:
        return [
            f"https://github.com/{self.repo}/archive/{self.vtag}.tar.gz#{self.name}.tar.gz",
            f"https://github.com/hchunhui/librime-lua/archive/{self.lub_plugin_rev}.tar.gz#librime-lua.tar.gz",
        ]

    def _metadata(self) -> T.Dict[str, str]:
        return dict(lua_plugin_vtag=self.lub_plugin_rev, **super()._metadata())
