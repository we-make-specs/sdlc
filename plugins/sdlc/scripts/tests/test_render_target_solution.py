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


REVISION = "0123456789abcdef0123456789abcdef01234567"


class TargetSolutionRenderingTest(unittest.TestCase):
    def test_rendering_is_byte_deterministic(self):
        self.assertEqual(MODULE.render_html(SOURCE).encode(), MODULE.render_html(SOURCE).encode())

    def test_complete_document_is_visible_and_navigable(self):
        page = MODULE.render_html(SOURCE)
        for text in ("Overview", "Target conceptual model", "Target flows", "Testing Strategy"):
            self.assertIn(text, page)
        self.assertIn("Nothing has been shortened or hidden", page)
        self.assertNotIn("<details", page)

    def test_nested_lists_preserve_order_and_continuation(self):
        source = """# Target

- **Happy path:**
  - Start the export
    after the request is accepted.
    3. Read the allocation.
       Keep its ID.
    4. Queue the event.
- **Edge cases:**
  - Reject a missing account.

After the list.
"""
        page = MODULE.render_html(source)
        self.assertIn(
            "<ul><li><strong>Happy path:</strong>\n"
            "<ul><li>Start the export after the request is accepted.\n"
            '<ol start="3"><li>Read the allocation. Keep its ID.</li>'
            "<li>Queue the event.</li></ol></li></ul></li>"
            "<li><strong>Edge cases:</strong>\n"
            "<ul><li>Reject a missing account.</li></ul></li></ul>",
            page,
        )
        self.assertIn("</ul>\n<p>After the list.</p>", page)

    def test_indented_paragraphs_and_fences_stay_in_the_item(self):
        source = """# Target

1. Check the service.

   It returns a response.

   ````text
   first

   ```
   last
   ````
2. Record the result.
"""
        page = MODULE.render_html(source)
        self.assertIn(
            "<ol><li><p>Check the service.</p>\n<p>It returns a response.</p>\n"
            '<div class=code-block><div class=code-label>text</div>'
            "<pre><code class='language-text'>first\n\n```\nlast</code></pre></div></li>"
            "<li>Record the result.</li></ol>",
            page,
        )

    def test_table_cell_lists_render_safe_inline_markup(self):
        source = r"""# Target

| Change | Outcomes |
|---|---|
| A \| B | - Keep **one**<br>- See [`source`](notes.md)<br/>- Escape <script>alert(1)</script> |
"""
        page = MODULE.render_html(source)
        self.assertIn(
            '<td>A | B</td><td><ul><li>Keep <strong>one</strong></li>'
            '<li>See <a href="notes.md"><code>source</code></a></li>'
            '<li>Escape &lt;script&gt;alert(1)&lt;/script&gt;</li></ul></td>',
            page,
        )

    def test_table_cell_list_labels_and_literal_breaks(self):
        source = """| Choice | Trade-offs |
|---|---|
| A | **Benefit**<br>- One<br>- Two<br>**Cost**<br>- Keep literal `<br>`<br>- Escape <br onclick="bad()"> |
"""
        page = MODULE.render_html(source)
        self.assertIn(
            "<td><p><strong>Benefit</strong></p><ul><li>One</li><li>Two</li></ul>"
            "<p><strong>Cost</strong></p><ul><li>Keep literal <code>&lt;br&gt;</code></li>"
            "<li>Escape &lt;br onclick=&quot;bad()&quot;&gt;</li></ul></td>",
            page,
        )

    def test_annotated_code_is_visible_with_a_matching_enterprise_link(self):
        url = f"https://github.example/org/repo/blob/{REVISION}/src/example%20file.py#L42-L43"
        source = (
            "# Target\n\nSee [`B1`](#ref-B1).\n\n"
            f"```python ref=B1 path='src/example file.py' lines=42-43 revision={REVISION} url={url}\n"
            "if value < 3:\n"
            "    show('<script>')\n"
            "```\n"
        )
        page = MODULE.render_html(source)
        self.assertEqual(page, MODULE.render_html(source))
        self.assertIn('<a href="#ref-B1"><code>B1</code></a>', page)
        self.assertIn('<figure class="source-preview" id="ref-B1">', page)
        self.assertIn("<code>src/example file.py:42-43</code>", page)
        self.assertIn(f'title="{REVISION}"', page)
        self.assertIn(f'<a href="{url}">Open source</a>', page)
        self.assertIn("if value &lt; 3:\n    show(&#x27;&lt;script&gt;&#x27;)", page)
        self.assertNotIn("<details", page)
        self.assertNotIn("<script", page)

    def test_annotated_code_can_use_one_line_without_a_link(self):
        source = f"```text ref=B1 path=src/example.txt lines=42 revision={REVISION}\nvalue\n```"
        page = MODULE.render_html(source)
        self.assertIn('<figure class="source-preview" id="ref-B1">', page)
        self.assertIn("src/example.txt:42", page)
        self.assertNotIn("Open source", page)
        with self.assertRaisesRegex(ValueError, "duplicate code reference ID B1"):
            MODULE.render_html(f"{source}\n\n{source}")

    def test_annotated_code_rejects_invalid_metadata(self):
        info = f"text ref=B1 path=src/example.txt lines=42 revision={REVISION}"
        invalid = [
            (info.replace("path=src/example.txt", "path=/src/example.txt"), "path must be relative"),
            (info.replace("path=src/example.txt", "path=src/../example.txt"), "path must be relative"),
            (info.replace("path=src/example.txt", r"path=src\example.txt"), "cannot contain backslashes"),
            (info.replace(REVISION, REVISION[:8]), "full 40-character commit"),
            (info.replace("lines=42", "lines=42-43"), "does not match"),
            (info.replace("lines=42", "lines=0"), "positive line or range"),
            (info.replace("ref=B1", "ref B1"), "invalid or repeated attribute"),
            (info.replace(" lines=42", ""), "requires ref, path, lines and revision"),
            (info + " ref=B2", "invalid or repeated attribute"),
            (info + ' url="https://github.example', "invalid code reference metadata"),
        ]
        for metadata, error in invalid:
            with self.subTest(metadata=metadata), self.assertRaisesRegex(ValueError, error):
                MODULE.render_html(f"```{metadata}\nvalue\n```")
        with self.assertRaisesRegex(ValueError, "unclosed code reference fence"):
            MODULE.render_html(f"```{info}\nvalue")

    def test_annotated_code_rejects_nonmatching_or_unsafe_links(self):
        info = f"text ref=B1 path=src/example.txt lines=42 revision={REVISION}"
        link = f"https://github.example/org/repo/blob/{REVISION}/src/example.txt#L42"
        invalid = [
            link.replace("https:", "http:"),
            link.replace("github.example", "user@github.example"),
            link.replace("src/example.txt", "src/other.txt"),
            link.replace("#L42", "#L43"),
            link.replace(REVISION, "f" * 40),
            link.replace("#", "?token=secret#"),
            "javascript:alert(1)",
        ]
        for url in invalid:
            with self.subTest(url=url), self.assertRaisesRegex(ValueError, "code reference URL"):
                MODULE.render_html(f"```{info} url={url}\nvalue\n```")

    def test_unclosed_ordinary_fence_preserves_its_content(self):
        source = '# Target\n\n```text title="literal ref=B1"\n<em>not markup</em>\nlast'
        page = MODULE.render_html(source)
        self.assertIn("&lt;em&gt;not markup&lt;/em&gt;\nlast", page)
        self.assertNotIn('<figure class="source-preview"', page)

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
