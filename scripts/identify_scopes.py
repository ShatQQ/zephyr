#!/usr/bin/env python3

# Copyright (c) 2023, Baumer (Baumer.com)
# SPDX-License-Identifier: Apache-2.0

"""
Lists scopes for different areas of the Zephyr project and

The comment at the top of scope.yml in Zephyr documents the file format.

    ./identify_scopes.py path --help

This executable doubles as a Python library. Identifiers not prefixed with '_'
are part of the library API. The library documentation can be viewed with this
command:

    $ pydoc get_scope
"""

import argparse
import operator
import os
import pathlib
import re
import shlex
import subprocess
import sys

from yaml import load, YAMLError
try:
    # Use the speedier C LibYAML parser if available
    from yaml import CSafeLoader as SafeLoader
except ImportError:
    from yaml import SafeLoader


def _main():
    # Entry point when run as an executable

    args = _parse_args()
    try:
        args.cmd_fn(Scope(args.scopes), args)
    except (ScopeError, GitError) as e:
        _serr(e)


def _parse_args():
    # Parses arguments when run as an executable

    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=__doc__, allow_abbrev=False)

    parser.add_argument(
        "-s", "--scopes",
        metavar="SCOPE_FILE",
        help="Scope file to load. If not specified, scope.yml in "
             "the top-level repository directory is used, and must exist. "
             "Paths in the scope file will always be taken as relative "
             "to the top-level directory.")

    subparsers = parser.add_subparsers(
        help="Available commands (each has a separate --help text)")

    id_parser = subparsers.add_parser(
        "area",
        help="List area(s) for paths")
    id_parser.add_argument(
        "paths",
        metavar="PATH",
        nargs="*",
        help="Path to list scope for")
    id_parser.set_defaults(cmd_fn=Scope._path_cmd)

    list_parser = subparsers.add_parser(
        "list",
        help="List files in scope")
    list_parser.add_argument(
        "scope",
        metavar="SCOPE",
        nargs="?",
        help="Name of scope to list files in. If not specified, all "
             "non-orphaned files are listed (all files that do not appear in "
             "any scope).")
    list_parser.set_defaults(cmd_fn=Scope._list_cmd)

    args = parser.parse_args()
    if not hasattr(args, "cmd_fn"):
        # Called without a subcommand
        sys.exit(parser.format_usage().rstrip())

    return args


class Scope:
    """
    Represents an entry for an scope in scope.yml.

    These attributes are available:

    filename:
       The path to the scope file

    group:
        The group of the scope, as a string. None if the area has no 'status'
        key. See scope.yml.

    labels:
        List of GitHub labels for the area. Empty if the area has no 'labels'
        key.

    description:
        Text from 'description' key, or None if the area has no 'description'
        key
    """
    def __init__(self, filename=None):
        """
        Creates a scope instance.

        filename (default: None):
            Path to the maintainers file to parse. If None, scope.yml in
            the top-level directory of the Git repository is used, and must
            exist.
        """
        self._toplevel = pathlib.Path(_git("rev-parse", "--show-toplevel"))
        print(self._toplevel)

        if filename is None:
            self.filename = self._toplevel / "scope.yml"
        else:
            self.filename = pathlib.Path(filename)

        self.scopes = {}
        for scope_name, scope_dict in _load_scopes(self.filename).items():
            scope = Scope()
            scope.name = scope_name
            print(scope_name)
            print(scope_dict.get("files", []))
            print(scope_dict.get("labels", []))
            print(scope_dict.get("description"))
            print(scope_dict)

            self.scopes[scope_name] = area

    def __repr__(self):
        return "<Scope {}>".format(self.name)

    #
    # Command-line subcommands
    #

    def _path_cmd(self, args):
        # 'path' subcommand implementation

        print("Im the path command")

    def _list_cmd(self, args):
        # 'path' subcommand implementation

        print("Im the list command")


def _load_scopes(path):
    # Returns the parsed contents of the scope file 'filename', also
    # running checks on the contents. The returned format is plain Python
    # dicts/lists/etc., mirroring the structure of the file.

    with open(path, encoding="utf-8") as f:
        try:
            yaml = load(f, Loader=SafeLoader)
        except YAMLError as e:
            raise ScopeError("{}: YAML error: {}".format(path, e))
        return yaml


def _git(*args):
    # Helper for running a Git command. Returns the rstrip()ed stdout output.
    # Called like git("diff"). Exits with SystemError (raised by sys.exit()) on
    # errors.

    git_cmd = ("git",) + args
    git_cmd_s = " ".join(shlex.quote(word) for word in git_cmd)  # For errors

    try:
        git_process = subprocess.Popen(
            git_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        _giterr("git executable not found (when running '{}'). Check that "
                "it's in listed in the PATH environment variable"
                .format(git_cmd_s))
    except OSError as e:
        _giterr("error running '{}': {}".format(git_cmd_s, e))

    stdout, stderr = git_process.communicate()
    if git_process.returncode:
        _giterr("error running '{}'\n\nstdout:\n{}\nstderr:\n{}".format(
            git_cmd_s, stdout.decode("utf-8"), stderr.decode("utf-8")))

    return stdout.decode("utf-8").rstrip()

def _err(msg):
    raise ScopeError(msg)

def _giterr(msg):
    raise GitError(msg)



def _serr(msg):
    # For reporting errors when get_maintainer.py is run as a script.
    # sys.exit() shouldn't be used otherwise.
    sys.exit("{}: error: {}".format(sys.argv[0], msg))


class ScopeError(Exception):
    "Exception raised for scope.yml-related errors"

class GitError(Exception):
    "Exception raised for Git-related errors"



if __name__ == "__main__":
    _main()
