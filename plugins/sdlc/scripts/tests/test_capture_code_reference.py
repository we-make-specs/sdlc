import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


sys.path.insert(0, str(Path(__file__).parents[1]))

from capture_code_reference import capture_reference
from render_target_solution import render_html


class CaptureCodeReferenceTest(unittest.TestCase):
    def test_captures_only_the_selected_commit_and_lines(self):
        with tempfile.TemporaryDirectory() as directory:
            repo = Path(directory)
            path = repo / "example file.txt"
            path.write_text("before\nkeep\n```\nafter\n", encoding="utf-8")
            subprocess.run(["git", "init", "-q", str(repo)], check=True, capture_output=True)
            subprocess.run(["git", "-C", str(repo), "add", path.name], check=True, capture_output=True)
            subprocess.run(
                [
                    "git", "-C", str(repo),
                    "-c", "user.name=Example",
                    "-c", "user.email=example@example.com",
                    "-c", "commit.gpgSign=false",
                    "commit", "-qm", "Record source",
                ],
                check=True,
                capture_output=True,
            )
            commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
            path.write_text("local edits\n", encoding="utf-8")

            block = capture_reference(repo, "B1", path.name, "2-3", "HEAD", "text", "https://github.example/org/repo")
            self.assertTrue(block.startswith("````text "))
            self.assertIn("\nkeep\n```\n````\n", block)
            page = render_html(block)
            self.assertIn(f"https://github.example/org/repo/blob/{commit}/example%20file.txt#L2-L3", page)
            self.assertIn("keep\n```", page)
            self.assertNotIn("local edits", page)
            with self.assertRaisesRegex(ValueError, "outside"):
                capture_reference(repo, "B1", path.name, "5", "HEAD", "text")


if __name__ == "__main__":
    unittest.main()
