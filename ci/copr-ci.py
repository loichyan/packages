#!/usr/bin/env python

import argparse
import os
import requests


class EnvDefault(argparse.Action):
    def __init__(self, envvar, required=True, default=None, **kwargs):
        if not default and envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required, **kwargs)

    def __call__(self, _, namespace, values):
        setattr(namespace, self.dest, values)


parser = argparse.ArgumentParser()
parser.add_argument(
    "--user-id",
    metavar="ID",
    action=EnvDefault,
    envvar="COPR_USER_ID",
)
parser.add_argument(
    "--project-uuid",
    metavar="UUID",
    action=EnvDefault,
    envvar="COPR_PROJECT_UUID",
)
parser.add_argument(
    "package",
    metavar="PACKAGE",
)
args = parser.parse_args()

requests.post(
    f"https://copr.fedorainfracloud.org/webhooks/custom/{args.user_id}/{args.project_uuid}/{args.package}/"
)
