"""Tests for check_pr_title.py. Run them with: python3 -m unittest discover -s scripts"""
import json
import os
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_pr_title  # noqa: E402

SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "check_pr_title.py")
TYPES = {"feat", "fix", "docs", "build", "ci", "revert"}
SCOPES = {"intent", "build", "plugin"}


class Titles(unittest.TestCase):
    def assert_passes(self, titles):
        for title in titles:
            with self.subTest(title=title):
                self.assertEqual(check_pr_title.check_title(title, TYPES, SCOPES), [])

    def assert_fails(self, titles, expected):
        for title in titles:
            with self.subTest(title=title):
                findings = check_pr_title.check_title(title, TYPES, SCOPES)
                self.assertTrue(any(expected in finding for finding in findings), findings)

    def test_valid_titles_pass(self):
        self.assert_passes([
            "feat(intent): ask for the affected systems in the intent template",
            "ci: check pull request titles",
            "feat!: read commit scopes from .wongchon/config.json",
            "fix(build)!: keep multiline PR descriptions in the plan hook",
            "build(build): pin Python to 3.9",
            "revert(intent): ask for the affected systems in the intent template",
            "docs: " + "a" * 66,
        ])

    def test_bad_form_fails(self):
        self.assert_fails([
            "add a CI gate",
            "feat:add a CI gate",
            "feat : add a CI gate",
            "feat !: add a CI gate",
            "feat(intent) : add a CI gate",
            "feat(intent)!:  add a CI gate",
            "feat(intent: add a CI gate",
            "feat(): ",
        ], "does not have the form")

    def test_unknown_type_fails(self):
        self.assert_fails(["feature: add a CI gate", "Feat: add a CI gate", "wip: add a CI gate"],
                          "is not in the Types table")

    def test_unknown_or_combined_scope_fails(self):
        self.assert_fails([
            "feat(stage): add a CI gate",
            "feat(intent,build): add a CI gate",
            "feat(intent, build): add a CI gate",
            "feat(): add a CI gate",
        ], "is not in commit.scopes")

    def test_description_must_start_lowercase(self):
        self.assert_fails(["feat: Add a CI gate", "feat: 3 checks in CI"], "lowercase letter")

    def test_description_must_not_end_with_period(self):
        self.assert_fails(["feat: add a CI gate."], "ends with a period")

    def test_description_must_be_plain_text(self):
        self.assert_fails([
            "feat: add the `check_pr_title.py` script",
            "docs: link the [playbook](https://example.com)",
            "docs: link https://example.com in the roadmap",
        ], "Write plain text")

    def test_long_title_fails(self):
        self.assert_fails(["docs: " + "a" * 67], "more than 72")


class Rules(unittest.TestCase):
    def test_types_come_from_the_convention(self):
        self.assertEqual(check_pr_title.load_types(), {
            "feat", "fix", "docs", "refactor", "test", "perf", "build", "ci", "style", "chore", "revert"})

    def test_types_without_a_table_fail(self):
        with tempfile.NamedTemporaryFile("w", suffix=".md", delete=False) as file:
            file.write("# Commit message conventions\n\n| `feat` | Add functionality |\n")
        self.addCleanup(os.remove, file.name)
        with self.assertRaises(ValueError):
            check_pr_title.load_types(file.name)

    def test_scopes_come_from_the_config(self):
        with tempfile.TemporaryDirectory() as directory:
            path = os.path.join(directory, "config.json")
            with open(path, "w") as file:
                json.dump({"commit": {"scopes": [{"name": "intent", "area": "", "paths": []}]}}, file)
            self.assertEqual(check_pr_title.load_scopes(path), {"intent"})
            self.assertEqual(check_pr_title.load_scopes(os.path.join(directory, "missing.json")), set())


class Script(unittest.TestCase):
    def run_script(self, title):
        env = dict(os.environ)
        env.pop("PR_TITLE", None)
        if title is not None:
            env["PR_TITLE"] = title
        root = os.path.join(os.path.dirname(SCRIPT), os.pardir)
        return subprocess.run([sys.executable, SCRIPT], cwd=root, env=env,
                              stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

    def test_good_title_exits_0(self):
        self.assertEqual(self.run_script("feat(plugin): add the PR title check").returncode, 0)

    def test_bad_title_exits_1_with_findings(self):
        result = self.run_script("Feature(ci): Add the PR title check.")
        self.assertEqual(result.returncode, 1)
        self.assertIn("is not in the Types table", result.stderr)
        self.assertIn('the scope "ci" is not in commit.scopes', result.stderr)
        self.assertIn("lowercase letter", result.stderr)

    def test_missing_title_exits_2(self):
        self.assertEqual(self.run_script(None).returncode, 2)


if __name__ == "__main__":
    unittest.main()
