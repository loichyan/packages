#!/usr/bin/env python

import argparse
import logging
import os
import re
import requests
import subprocess
from datetime import datetime

USER = "github-actions"
EMAIL = "41898282+github-actions[bot]@users.noreply.github.com"

parser = argparse.ArgumentParser()
parser.add_argument(
    "--user-id",
    metavar="ID",
)
parser.add_argument(
    "--project-uuid",
    metavar="UUID",
)
parser.add_argument(
    "--no-check",
    action="store_true",
)
parser.add_argument(
    "--no-push",
    action="store_true",
)
parser.add_argument(
    "--no-trigger",
    action="store_true",
)
parser.add_argument(
    "packages",
    nargs="*",
    metavar="PACKAGES",
)
args = parser.parse_args()


def arg_or_env(arg: str, env: str):
    def getter():
        val = getattr(args, arg) or os.environ.get(env)
        if val is None:
            raise Exception(f"Argument {arg.upper()} is not supplied")
        return val

    return getter


user_id = arg_or_env("user_id", "COPR_USER_UD")
project_uuid = arg_or_env("project_uuid", "COPR_PROJECT_UUID")


class Package:
    name: str
    repo: str
    _version: str

    def __init__(self, name: str, repo: str, *, version: str = r"^v(.+)$"):
        self.name = name
        self.repo = repo
        self._version = version

    @property
    def spec(self) -> str:
        if not hasattr(self, "_spec"):
            with open(f"{self.name}/{self.name}.spec") as f:
                self._spec = f.read()
        return self._spec

    @property
    def spec_tag(self):
        if not hasattr(self, "_spec_tag"):
            res = re.search(r"%global vtag (.+)$", self.spec, re.M)
            assert res, self.spec
            self._spec_tag = res.group(1)
        return self._spec_tag

    @property
    def latest_tag(self) -> str:
        if not hasattr(self, "_latest_tag"):
            resp = requests.get(
                f"https://api.github.com/repos/{self.repo}/releases/latest"
            ).json()
            self._latest_tag = resp["tag_name"]
        return self._latest_tag

    @property
    def latest_version(self) -> str:
        if not hasattr(self, "_latest_version"):
            v = re.sub(self._version, r"\1", self.latest_tag)
            self._latest_version = v
        return self._latest_version

    def update(self):
        """
        Trigger Copr to rebuild a package if a new version is found.
        """
        if not args.no_check:
            if self.check():
                logging.info(f"Skip latest package {self.name}")
                return
        if args.no_trigger:
            return
        self.trigger_rebuild()

    def check(self) -> bool:
        """
        Return whether this package is latest.
        """

        logging.info(f"Check update of package {self.name}")
        if self.spec_tag != self.latest_tag:
            logging.info(
                f"Update version of package {self.name} from {self.spec_tag} to {self.latest_tag}"
            )
            self._update_spec()
            self._update_changelog()
            self._commit_changes()
            return False
        return True

    def _update_spec(self):
        path = f"{self.name}/{self.name}.spec"
        logging.info(f"Update {path}")
        spec = ""
        with open(path, "r") as f:
            spec = f.read()
        # Bump version tag
        spec = re.sub(r"(?<=%global vtag ).+", self.latest_tag, spec)
        # Reset release version
        spec = re.sub(r"(?<=%autorelease).*", "", spec)
        with open(path, "w") as f:
            f.write(spec)

    def _update_changelog(self):
        path = f"{self.name}/changelog"
        logging.info(f"Update {path}")
        now = datetime.now().strftime("%c")
        changelog = (
            f"* {now} {USER} <{EMAIL}> - {self.latest_version}-1\n"
            f"- Bump version tag to {self.latest_tag}\n"
        )
        with open(path, "r") as f:
            changelog = changelog + "\n" + f.read()
        with open(path, "w") as f:
            f.write(changelog)

    def _commit_changes(self):
        logging.info(f"Commit changes of {self.name}")
        subprocess.run(
            [
                "git",
                "-c",
                f"user.name={USER}",
                "-c",
                f"user.email={EMAIL}",
                "commit",
                "--all",
                "-m",
                f"chore({self.name}): bump version to {self.latest_version}",
            ]
        )
        if not args.no_push:
            logging.info(f"Push commits of {self.name}")
            subprocess.run(["git", "push"])

    def trigger_rebuild(self):
        logging.info(f"Trigger rebuild of package {self.name}")
        requests.post(
            f"https://copr.fedorainfracloud.org/webhooks/custom/{user_id()}/{project_uuid()}/{self.name}/"
        )


packages = {
    "wezterm": Package("wezterm", "wez/wezterm", version=r"^(\d+).*$"),
    "symbols-nerd-font": Package("symbols-nerd-font", "ryanoasis/nerd-fonts"),
}
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

try:
    pkgs = set(args.packages)
    if len(pkgs) == 0:
        for pkg in packages.values():
            pkg.update()
    else:
        for name in pkgs:
            pkg = packages.get(name)
            if not pkg:
                raise Exception(f"Package {name} is undefined")
            pkg.update()
except Exception as e:
    logging.error(f"Error: {e}")
    raise (e)
