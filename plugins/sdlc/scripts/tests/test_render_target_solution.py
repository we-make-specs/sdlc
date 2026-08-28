import importlib.util
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "render_target_solution.py"
SPEC = importlib.util.spec_from_file_location("render_target_solution", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(MODULE)


SOURCE = """# Target Solution: Safe export

- **Status:** IN REVIEW

## Overview

The service exports `<safe>` data through the outbox.

## Target conceptual model

| Concept | Meaning |
|---|---|
| Batch | One ordered export |

## Target flows

1. Read the allocation.
2. Queue the event.

## Testing Strategy

```bash
./gradlew test
```
"""


class TargetSolutionRenderingTest(unittest.TestCase):
    def test_rendering_is_byte_deterministic(self):
        self.assertEqual(MODULE.render_html(SOURCE).encode(), MODULE.render_html(SOURCE).encode())

    def test_complete_document_is_visible_and_navigable(self):
        page = MODULE.render_html(SOURCE)
        for text in ("Overview", "Target conceptual model", "Target flows", "Testing Strategy"):
            self.assertIn(text, page)
        self.assertIn("Nothing has been shortened or hidden", page)
        self.assertNotIn("<details", page)

    def test_source_content_is_escaped(self):
        page = MODULE.render_html(SOURCE)
        self.assertIn("&lt;safe&gt;", page)
        self.assertNotIn("<safe>", page)

    def test_executable_link_schemes_are_rejected_case_insensitively(self):
        for href in ("JaVaScRiPt:alert(1)", "  data:text/html,x", "vbscript:msgbox(1)", "//evil.example/x"):
            page = MODULE.render_html(f"# Target\n\n[click]({href})")
            self.assertNotIn("javascript:", page.casefold())
            self.assertNotIn("data:text/html", page.casefold())
            self.assertNotIn("vbscript:", page.casefold())
            self.assertNotIn("evil.example", page.casefold())

    def test_relative_and_https_links_remain_available(self):
        page = MODULE.render_html("# Target\n\n[local](notes/design.md) [web](https://example.com)")
        self.assertIn('href="notes/design.md"', page)
        self.assertIn('href="https://example.com"', page)


if __name__ == "__main__":
    unittest.main()
