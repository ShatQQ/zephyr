#!/usr/bin/env python3

# Copyright (c) 2023, Baumer (Baumer.com)
# SPDX-License-Identifier: Apache-2.0

"""
Lists scopes for different areas of the Zephyr project and

The comment at the top of scope.yml in Zephyr documents the file format.

    ./identify_scopes.py list --help

This executable doubles as a Python library. Identifiers not prefixed with '_'
are part of the library API. The library documentation can be viewed with this
command:

    $ pydoc get_scope
"""

import argparse
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
        args.cmd_fn(Scopes(args.scopes), args)
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
    list_parser.set_defaults(cmd_fn=Scopes._list_cmd)

    args = parser.parse_args()
    if not hasattr(args, "cmd_fn"):
        # Called without a subcommand
        sys.exit(parser.format_usage().rstrip())

    return args


class Scopes:
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
        Creates a scopes instance.

        filename (default: None):
            Path to the scope file to parse. If None, scope.yml in
            the top-level directory of the Git repository is used, and must
            exist.
        """
        self._toplevel = pathlib.Path(_git("rev-parse", "--show-toplevel"))

        if filename is None:
            self.filename = self._toplevel / "scope.yml"
        else:
            self.filename = pathlib.Path(filename)

        self.scopes = {}
        for scope_name, scope_dict in _load_scopes(self.filename).items():
            area = Area()
            area.name = scope_name
            area.files = scope_dict.get("files", [])
            area.labels = scope_dict.get("labels", [])
            area.description = scope_dict.get("description")

            # area._match_fn(path) tests if the path matches files and/or
            # files-regex
            area._match_fn = \
                _get_match_fn(scope_dict.get("files"),
                              scope_dict.get("files-regex"))

            # Like area._match_fn(path), but for files-exclude and
            # files-regex-exclude
            area._exclude_match_fn = \
                _get_match_fn(scope_dict.get("files-exclude"),
                              scope_dict.get("files-regex-exclude"))

            self.scopes[scope_name] = area

    def __repr__(self):
        return "<Scope {}>".format(self.name)

    #
    # Command-line subcommands
    #

    def _list_cmd(self, args):
        # 'list' subcommand implementation

        scopelist = []

        if args.scope is None:
            # List all files that appear in some area
            for path in _ls_files():
                for area in self.scopes.values():
                    if area._contains(path):
                        print(path)
                        scopelist.append(path)
                        break
        else:
            # List all files that appear in the given area
            area = self.scopes.get(args.scope)
            if area is None:
                _serr("'{}': no such area defined in '{}'"
                      .format(args.scope, self.filename))

            for path in _ls_files():
                if area._contains(path):
                    scopelist.append(path)
                    print(path)

        return scopelist

class Area:

    def _contains(self, path):
        # Returns True if the area contains 'path', and False otherwise

        return self._match_fn and self._match_fn(path) and not \
            (self._exclude_match_fn and self._exclude_match_fn(path))

    def __repr__(self):
        return "<Area {}>".format(self.name)


def _get_match_fn(globs, regexes):
    # Constructs a single regex that tests for matches against the globs in
    # 'globs' and the regexes in 'regexes'. Parts are joined with '|' (OR).
    # Returns the search() method of the compiled regex.
    #
    # Returns None if there are neither globs nor regexes, which should be
    # interpreted as no match.

    if not (globs or regexes):
        return None

    regex = ""

    if globs:
        glob_regexes = []
        for glob in globs:
            # Construct a regex equivalent to the glob
            glob_regex = glob.replace(".", "\\.").replace("*", "[^/]*") \
                             .replace("?", "[^/]")

            if not glob.endswith("/"):
                # Require a full match for globs that don't end in /
                glob_regex += "$"

            glob_regexes.append(glob_regex)

        # The glob regexes must anchor to the beginning of the path, since we
        # return search(). (?:) is a non-capturing group.
        regex += "^(?:{})".format("|".join(glob_regexes))

    if regexes:
        if regex:
            regex += "|"
        regex += "|".join(regexes)

    return re.compile(regex).search

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

def _ls_files(path=None):
    cmd = ["ls-files"]
    if path is not None:
        cmd.append(path)
    return _git(*cmd).splitlines()

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

def _giterr(msg):
    raise GitError(msg)

def _serr(msg):
    # For reporting errors when identif_scopes.py is run as a script.
    # sys.exit() shouldn't be used otherwise.
    sys.exit("{}: error: {}".format(sys.argv[0], msg))

class ScopeError(Exception):
    "Exception raised for scope.yml-related errors"

class GitError(Exception):
    "Exception raised for Git-related errors"

if __name__ == "__main__":
    _main()
