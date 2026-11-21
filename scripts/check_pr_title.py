#!/usr/bin/env python3
"""Check a pull request title against the subject rules of the commit message conventions.

Run this script from the root of the project. It reads the title from the PR_TITLE
environment variable, so that a CI workflow never puts the title inside a shell script.
It takes the types from the Types table of docs/conventions/commit-messages.md next to
this script, and the scope names from commit.scopes in .wongchon/config.json of the
project. The script checks:

- the form <type>(<scope>)!: <description>, with an optional scope and breaking marker.
- a type from the Types table, and a scope name from commit.scopes.
- a description that starts with a lowercase letter, does not end with a period, and
  has no backticks, Markdown links, or URLs.
- a subject line of at most 72 characters.

A script cannot tell if a description uses the imperative mood or names a specific
change, so the maintainer checks these rules in review.

If the title breaks a rule, the script writes each finding to standard error and exits
with code 1.
"""
import json
import os
import re
import sys

CONVENTION = os.path.join(os.path.dirname(os.path.abspath(__file__)), os.pardir,
                          "docs", "conventions", "commit-messages.md")
CONFIG = os.path.join(".wongchon", "config.json")
MAX_LENGTH = 72
SUBJECT = re.compile(r"^(?P<type>[^\s():!]+)(?:\((?P<scope>[^()]*)\))?(?P<breaking>!)?: (?P<description>\S.*)$")
TYPE_ROW = re.compile(r"^\|\s*`([^`]+)`\s*\|")
MARKUP = re.compile(r"`|\]\(|://")


def load_types(path=CONVENTION):
    """Return the types in the Types table of the commit message conventions."""
    types = set()
    in_table = False
    with open(path, encoding="utf-8") as file:
        for line in file:
            if line.startswith("#"):
                in_table = line.strip() == "### Types"
            elif in_table:
                match = TYPE_ROW.match(line)
                if match:
                    types.add(match.group(1))
    if not types:
        raise ValueError("cannot read the Types table of {0}".format(path))
    return types


def load_scopes(path=CONFIG):
    """Return the scope names in commit.scopes. Without the file or the list, no scope is valid."""
    if not os.path.exists(path):
        return set()
    with open(path, encoding="utf-8") as file:
        config = json.load(file)
    return {scope["name"] for scope in config.get("commit", {}).get("scopes", [])}


def check_title(title, types, scopes):
    """Return the findings for the title. An empty list means that the title follows the rules."""
    match = SUBJECT.match(title)
    if not match:
        return ['"{0}" does not have the form <type>(<scope>)!: <description>, '
                "with an optional scope and !".format(title)]
    findings = []
    if match.group("type") not in types:
        findings.append('the type "{0}" is not in the Types table. Use one of: {1}'.format(
            match.group("type"), ", ".join(sorted(types))))
    scope = match.group("scope")
    if scope is not None and scope not in scopes:
        findings.append('the scope "{0}" is not in commit.scopes of {1}. Use one scope name of: {2}, '
                        "or omit the scope".format(scope, CONFIG, ", ".join(sorted(scopes)) or "none"))
    description = match.group("description")
    if not description[0].islower():
        findings.append("the description does not start with a lowercase letter")
    if description.endswith("."):
        findings.append("the description ends with a period")
    if MARKUP.search(description):
        findings.append("the description has a backtick, a Markdown link, or a URL. Write plain text")
    if len(title) > MAX_LENGTH:
        findings.append("the title has {0} characters, more than {1}".format(len(title), MAX_LENGTH))
    return findings


def main():
    title = os.environ.get("PR_TITLE")
    if not title:
        print("Set the PR_TITLE environment variable to the pull request title.", file=sys.stderr)
        sys.exit(2)
    findings = check_title(title, load_types(), load_scopes())
    if findings:
        print("The PR title does not follow docs/conventions/commit-messages.md:", file=sys.stderr)
        for finding in findings:
            print("- " + finding, file=sys.stderr)
        sys.exit(1)
    print("The PR title follows the subject rules.")


if __name__ == "__main__":
    main()
