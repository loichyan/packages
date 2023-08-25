from lib import GhPackage, cmd
from os.path import join
import typing as T
import os
import shutil as sh


class Package(GhPackage):
    def __init__(self):
        super().__init__("v2raya", "v2rayA/v2rayA")

    def _sources(self) -> T.List[str]:
        return [
            f"https://github.com/{self.repo}/archive/{self.vtag}.tar.gz#v2rayA-{self.version}",
        ]

    def _post_unpack(self):
        cwd = os.getcwd()
        # Build gui
        args: T.Dict[str, T.Any] = dict(
            cwd="gui",
            env={
                "NODE_OPTIONS": "--openssl-legacy-provider",
                "OUTPUT_DIR": f"{cwd}/service/server/router/web",
            },
        )
        cmd("yarn", "--check-files", **args)
        cmd("yarn", "build", **args)
        sh.rmtree(join("gui", "node_modules"))
        # Vendor dependencies for offline build
        cmd("go", "mod", "vendor", cwd="service")
