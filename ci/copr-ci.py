#!/usr/bin/env python

import argparse
import logging
import os
import re
import requests
import subprocess
from functools import cached_property
from datetime import datetime
import typing as T


COMMIT_USERNAME = "github-actions[bot]"
COMMIT_EMAIL = "github-actions[bot]@users.noreply.github.com"


def git(*args: str):
    subprocess.run(
        [
            "git",
            "-c",
            f"user.name={COMMIT_USERNAME}",
            "-c",
            f"user.email={COMMIT_EMAIL}",
            *args,
        ]
    ).check_returncode()


class Args:
    def __init__(self, envargs: T.Dict[str, str] = {}) -> None:
        object.__setattr__(self, "$envargs", envargs)

    def __getattribute__(self, arg: str):
        envarg = object.__getattribute__(self, "$envargs").get(arg)
        val = object.__getattribute__(self, arg)
        if envarg is not None and val is None:
            val = os.environ.get(envarg)
            if val is None:
                raise Exception(f"Argument {arg.upper()} is not supplied")
            object.__setattr__(self, arg, val)
        return val


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
args = parser.parse_args(
    namespace=Args(
        {
            "user_id": "COPR_USER_ID",
            "project_uuid": "COPR_PROJECT_UUID",
        }
    )
)


class Package:
    def __init__(
        self, name: str, repo: T.Optional[str] = None, *, version: str = r"^v(.+)$"
    ):
        self.name = name
        self.repo = repo
        self._version = version

    @cached_property
    def spec(self) -> str:
        with open(f"{self.name}/{self.name}.spec") as f:
            return f.read()

    @cached_property
    def spec_tag(self) -> str:
        res = re.search(r"%global vtag (.+)$", self.spec, re.M)
        assert res, f"Cannot find vtag in package {self.name}"
        return res.group(1)

    @cached_property
    def latest_tag(self) -> str:
        logging.info(f"Fetch the latest tag of package {self.name}")
        resp = requests.get(
            f"https://api.github.com/repos/{self.repo}/releases/latest"
        ).json()
        return resp["tag_name"]

    @cached_property
    def latest_version(self) -> str:
        return re.sub(self._version, r"\1", self.latest_tag)

    def update(self) -> bool:
        """
        Updates package, returns whether is updated.
        """
        if self.repo is None:
            return False
        if self.is_latest():
            logging.info(f"Skip latest package {self.name}")
            return False
        logging.info(
            f"Update package {self.name} from {self.spec_tag} to {self.latest_tag}"
        )
        self._update_spec()
        self._update_changelog()
        self._commit_changes()
        return True

    def is_latest(self) -> bool:
        """
        Returns whether this package is latest.
        """
        return self.spec_tag == self.latest_tag

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
            f"* {now} {COMMIT_USERNAME} <{COMMIT_EMAIL}> - {self.latest_version}-1\n"
            f"- Bump version tag to {self.latest_tag}\n"
        )
        with open(path, "r") as f:
            changelog = changelog + "\n" + f.read()
        with open(path, "w") as f:
            f.write(changelog)

    def _commit_changes(self):
        logging.info(f"Commit changes of {self.name}")
        git(
            "commit",
            "--all",
            "-m",
            f"chore({self.name}): bump version to {self.latest_version}",
        )

    @staticmethod
    def push_commits():
        logging.info(f"Push commits")
        git("push")

    def trigger_rebuild(self):
        logging.info(f"Trigger rebuild of package {self.name}")
        resp = requests.post(
            f"https://copr.fedorainfracloud.org/webhooks/custom/{args.user_id}/{args.project_uuid}/{self.name}/"
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Cannot rebuild package {self.name}: {resp.text}")


packages = {
    "wezterm": Package("wezterm", "wez/wezterm", version=r"^(\d+).*$"),
    "symbols-nerd-font": Package("symbols-nerd-font", "ryanoasis/nerd-fonts"),
    "nix-mount": Package("nix-mount"),
}
logging.basicConfig(format="%(levelname)s: %(message)s", level=logging.INFO)

try:
    assert args.user_id
    assert args.project_uuid
    pkgs = set(args.packages)
    # Collect packages to update
    pkgs_to_update: T.List[Package] = []
    if len(pkgs) == 0:
        pkgs_to_update.extend(packages.values())
    else:
        for name in pkgs:
            pkg = packages.get(name)
            if pkg is None:
                raise Exception(f"Package {name} is undefined")
            pkgs_to_update.append(pkg)
    pkgs_updated: T.List[Package] = (
        # Rebuild all packages if skip check
        pkgs_to_update
        if args.no_check
        # Else collect all updated packages
        else [pkg for pkg in pkgs_to_update if pkg.update()]
    )
    # Push commits if any
    if not args.no_push and not args.no_check and len(pkgs_updated) > 0:
        Package.push_commits()
    # Trigger rebuild
    if not args.no_trigger:
        for pkg in pkgs_updated:
            pkg.trigger_rebuild()
except Exception as e:
    logging.error(f"Error: {e}")
    raise (e)
