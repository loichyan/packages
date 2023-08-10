from lib import GhPackage, cmd
import typing as T
import os


class Package(GhPackage):
    def __init__(self):
        super().__init__("v2raya", "v2rayA/v2rayA")

    def _sources(self) -> T.List[str]:
        return [
            f"https://github.com/{self.repo}/archive/refs/tags/{self.vtag}.tar.gz#v2rayA-{self.version}",
        ]

    def _post_unpack(self):
        cwd = os.getcwd()
        # Build gui
        cmd(
            "yarn",
            "build",
            cwd="gui",
            env={
                "NODE_OPTIONS": "--openssl-legacy-provider",
                "OUTPUT_DIR": f"{cwd}/service/server/router/web",
            },
        )
        # Vendor dependencies for offline build
        cmd("go", "mod", "vendor", cwd="service")
