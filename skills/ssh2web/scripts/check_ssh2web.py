#!/usr/bin/env python3
"""Confirm the ssh2web CLI client is available, or print how to install it.

Offline, standard library only. Exit 0 when the ``ssh2web`` command is on PATH
and answers ``--version``; exit 1 (with the install command) when it is not.
"""
import shutil
import subprocess
import sys

REPO = "https://github.com/wservices/ssh2web"
INSTALL_CMD = "python3 -m pip install 'git+%s.git'" % REPO


def find_client():
    """Return the path to the ``ssh2web`` console script, or None."""
    return shutil.which("ssh2web")


def client_version(exe):
    """Return the client's ``--version`` text, or None if it could not run."""
    try:
        proc = subprocess.run(
            [exe, "--version"], capture_output=True, text=True, timeout=15
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return (proc.stdout or proc.stderr).strip() or "(no version string)"


def main(argv=None):
    exe = find_client()
    if not exe:
        print("ssh2web: not found on PATH.")
        print("Install it with:\n  " + INSTALL_CMD)
        return 1
    version = client_version(exe)
    if version is None:
        print("ssh2web: found at %s, but `--version` did not run." % exe)
        return 1
    print("ssh2web: %s" % exe)
    print("version: %s" % version)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
