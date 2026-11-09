import importlib.util
import unittest
from html.parser import HTMLParser
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "render_questions.py"
SPEC = importlib.util.spec_from_file_location("render_questions", MODULE_PATH)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


SOURCE = """# Questions: Export limits

## Important

### Q1 - [Important] [functional] File limit

- **Question:** How large may an export be?
- **Proposed answer:** A.
- **Answer:** <open>

| Option | Result | Trade-offs |
|---|---|---|
| A | Limit each file. | **Benefit**<br>- Bounded memory.<br>**Cost**<br>- More files. |
| B | Allow one large file. | **Benefit**<br>- One download.<br>**Cost**<br>- Higher memory use. |

### Q2 - [Important] [technical] Queue policy

- **Answer:** Assumed: retry once.
- **Confirmation:** pending

### Q3 - [Important] [functional] File format

- **Answer:** CSV. Rationale: existing consumers. User in review, 2026-11-09.

## Coverage record

Checked limits and retry behavior.
"""


class Elements(HTMLParser):
    def __init__(self, page):
        super().__init__()
        self.tags = []
        self.feed(page)

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class QuestionsRenderingTest(unittest.TestCase):
    def test_counts_and_entry_labels_come_from_answers(self):
        entries = MODULE.question_entries(SOURCE)
        self.assertEqual([item["status"] for item in entries], ["Open", "Needs confirmation", "Answered"])
        page = MODULE.render_html(SOURCE)
        for label in ("open", "needs confirmation", "answered"):
            self.assertIn(f"<b>1</b> {label}", page)
        for status in MODULE.STATUSES:
            self.assertEqual(page.count(f">{status}</span>"), 2)

    def test_all_options_remain_visible_without_controls_or_scripts(self):
        page = MODULE.render_html(SOURCE)
        self.assertIn("More files.", page)
        self.assertIn("Higher memory use.", page)
        self.assertIn("Coverage record", page)
        self.assertIn("<ul><li>Bounded memory.</li></ul>", page)
        tags = {tag for tag, _ in Elements(page).tags}
        self.assertFalse(tags & {"button", "input", "script", "details", "iframe"})

    def test_assumption_needs_verification_with_provenance(self):
        fields = {"answer": "Assumed: use UTC."}
        self.assertEqual(MODULE.answer_status(fields), "Needs confirmation")
        fields["confirmation"] = "verified"
        self.assertEqual(MODULE.answer_status(fields), "Needs confirmation")
        fields["confirmation"] = "verified by reviewer on 2026-11-09"
        self.assertEqual(MODULE.answer_status(fields), "Answered")

    def test_missing_input_cannot_be_closed_by_a_promise(self):
        fields = {"category": "Missing inputs", "answer": "Use the official schema.", "needed from": "API team"}
        self.assertEqual(MODULE.answer_status(fields), "Open")
        fields["input verification"] = "pending"
        self.assertEqual(MODULE.answer_status(fields), "Open")
        fields["input verification"] = "verified by reviewer on 2026-11-09; schema committed"
        self.assertEqual(MODULE.answer_status(fields), "Answered")

    def test_conditional_input_provider_does_not_reopen_a_decided_question(self):
        fields = {"category": "External dependencies", "needed from": "API team if B is chosen", "answer": "A: keep the existing interface."}
        self.assertEqual(MODULE.answer_status(fields), "Answered")

    def test_required_input_can_be_removed_by_a_recorded_decision(self):
        fields = {"category": "Missing inputs", "answer": "Keep the current format; redesign is a follow-up."}
        for verification in ("not required", "not required by reviewer on 2026-11-09"):
            fields["input verification"] = verification
            self.assertEqual(MODULE.answer_status(fields), "Open")
        fields["input verification"] = "not required by reviewer on 2026-11-09; redesign moved to a follow-up"
        self.assertEqual(MODULE.answer_status(fields), "Answered")

    def test_pending_correction_keeps_the_historical_answer_visible(self):
        source = "### Q1: Format\n- **Answer:** CSV.\n\n### Q2: Correction to Q1\n- **Context:** Reconsider the recorded CSV choice in Q1.\n- **Answer:** Open\n"
        self.assertEqual([item["status"] for item in MODULE.question_entries(source)], ["Answered", "Open"])
        self.assertIn("CSV.", MODULE.render_html(source))

    def test_plain_verification_fields_match_the_documented_forms(self):
        sources = (
            "### Q1: Source\n- **Category:** Missing inputs\n- **Answer:** Use the supplied schema.\n- Input verification: verified by reviewer on 2026-11-09\n",
            "### Q1: Zone\n- Answer: Assumed: UTC.\nConfirmation: verified by reviewer on 2026-11-09\n",
        )
        for source in sources:
            with self.subTest(source=source):
                self.assertEqual(MODULE.question_entries(source)[0]["status"], "Answered")

    def test_plain_fields_require_a_colon_and_share_duplicate_detection(self):
        source = "### Q1: Zone\n- **Answer:** Assumed: UTC.\nConfirmation verified by reviewer on 2026-11-09\n"
        self.assertEqual(MODULE.question_entries(source)[0]["status"], "Needs confirmation")
        duplicate = "### Q1: Zone\n- **Answer:** Open\n- Answer: UTC.\n"
        with self.assertRaisesRegex(ValueError, "duplicate answer"):
            MODULE.render_html(duplicate)

    def test_placeholder_answers_stay_open(self):
        for value in ("", "<open>", "TODO: ask owner", "Pending", "...", "<…>"):
            block = "### Q1: Title\n\n- **Answer:** " + value
            self.assertEqual(MODULE.question_entries(block)[0]["status"], "Open")
        self.assertEqual(MODULE.answer_status({"answer": "Open an issue for the missing connector."}), "Answered")

    def test_code_examples_are_not_questions_or_answer_fields(self):
        source = "### Q1: Title\n\n```text\n### Q2: Example\n- **Answer:** Fake\n```\n- **Answer:** Open\n"
        entries = MODULE.question_entries(source)
        self.assertEqual([(item["id"], item["status"]) for item in entries], [("Q1", "Open")])

    def test_non_question_heading_ends_answer_scope(self):
        source = "### Q1: Title\n\n- **Answer:** Open\n\n## Notes\n\n- **Confirmation:** pending\n"
        self.assertEqual(MODULE.question_entries(source)[0]["status"], "Open")

    def test_duplicate_ids_and_answer_fields_fail_instead_of_hiding_records(self):
        for source in ("### Q1: One\n\n### Q1: Two", "### Q1: One\n- **Answer:** A\n- **Answer:** B"):
            with self.assertRaises(ValueError):
                MODULE.render_html(source)

    def test_links_match_rendered_heading_ids_and_output_is_deterministic(self):
        page = MODULE.render_html(SOURCE)
        elements = Elements(page).tags
        ids = {attrs["id"] for _, attrs in elements if "id" in attrs}
        for tag, attrs in elements:
            if tag == "a" and attrs.get("href", "").startswith("#"):
                self.assertIn(attrs["href"][1:], ids)
        self.assertEqual(page, MODULE.render_html(SOURCE))
        self.assertIn("&lt;script&gt;", MODULE.render_html(SOURCE, title="<script>"))


if __name__ == "__main__":
    unittest.main()
