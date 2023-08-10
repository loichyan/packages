from lib import G, GhPackage, cmd, join
import typing as T


class Package(GhPackage):
    def __init__(self):
        super().__init__("wezterm", "wez/wezterm")

    def _parse_version(self, vtag: str) -> str:
        mat = G.PAT_WEZTERM_VERSION.match(vtag)
        assert mat is not None
        return mat[1]

    def _sources(self) -> T.List[str]:
        return [
            f"https://github.com/{self.repo}/releases/download/{self.vtag}/{self.name}-{self.vtag}-src.tar.gz#{self.name}-{self.vtag}"
        ]

    def _post_unpack(self):
        # Vendor dependencies for offline build
        config = cmd("cargo", "vendor")
        with open(join(".cargo", "config"), "a") as f:
            f.write(config)
