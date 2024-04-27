from functools import cached_property
from lib import GhPackage, G
import typing as T


class Package(GhPackage):
    def __init__(self):
        super().__init__("librime", "rime/librime")

    @cached_property
    def lua_plugin_vtag(self) -> str:
        return G.GH.get_repo("hchunhui/librime-lua").get_commit("master").sha

    def _parse_version(self, vtag: str) -> str:
        return vtag

    def _sources(self) -> T.List[str]:
        return [
            f"https://github.com/{self.repo}/archive/{self.vtag}.tar.gz#{self.name}.tar.gz",
            f"https://github.com/hchunhui/librime-lua/archive/{self.lua_plugin_vtag}.tar.gz#librime-lua.tar.gz",
        ]

    def _metadata(self) -> T.Dict[str, str]:
        return dict(lua_plugin_vtag=self.lua_plugin_vtag, **super()._metadata())
