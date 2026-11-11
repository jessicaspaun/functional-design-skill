"""Exercise the documented examples without introducing runtime dependencies."""

from pathlib import Path
import random
import re
import sys
import tempfile
from types import ModuleType
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills" / "functional-design"


class TrackingPath:
    """Track real file handles so resource assertions inspect actual cleanup."""

    def __init__(self, path):
        self.path = path
        self.handles = []

    def open(self, **kwargs):
        handle = self.path.open(**kwargs)
        self.handles.append(handle)
        return handle


class DocumentedExamples(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        text = (SKILL / "references" / "examples.md").read_text(encoding="utf-8")
        blocks = re.findall(r"```python\n(.*?)```", text, re.S)
        if not blocks:
            raise AssertionError("No Python examples found")
        cls.module = ModuleType("functional_design_documented_examples")
        sys.modules[cls.module.__name__] = cls.module
        for index, block in enumerate(blocks, start=1):
            exec(compile(block, f"documented-example-{index}", "exec"), cls.module.__dict__)

    @classmethod
    def tearDownClass(cls):
        sys.modules.pop(cls.module.__name__, None)

    def test_independent_validation_collects_both_errors(self):
        m = self.module
        outcome = m.plan_generation("   ", 0)
        self.assertIsInstance(outcome, m.Invalid)
        self.assertEqual(
            outcome.issues,
            ("prompt must contain text", "max_tokens must be positive"),
        )

    def test_plan_preserves_prompt_and_execution_calls_provider_once(self):
        m = self.module
        calls = []
        plan = m.plan_generation("  retain this spacing  ", 10)
        self.assertIsInstance(plan, m.Plan)
        self.assertEqual(plan.request.prompt, "  retain this spacing  ")
        self.assertEqual(calls, [])

        def provider(request):
            calls.append(request)
            return "document"

        self.assertEqual(m.execute(plan, provider), "document")
        self.assertEqual(calls, [plan.request])

    def test_state_transition_matches_reservation_invariants(self):
        m = self.module
        rng = random.Random(47191)
        for _ in range(1000):
            balance = rng.randint(0, 1000)
            amount = rng.randint(-10, 1200)
            initial = m.Budget(balance)
            with self.subTest(balance=balance, amount=amount):
                new, outcome = m.reserve(initial, amount)
                self.assertEqual(m.reserve(initial, amount), (new, outcome))
                self.assertEqual(initial.remaining, balance)
                if 0 < amount <= balance:
                    self.assertIsInstance(outcome, m.Reserved)
                    self.assertEqual(outcome.amount, amount)
                    self.assertEqual(new.remaining, balance - amount)
                else:
                    self.assertIsInstance(outcome, m.Invalid)
                    self.assertIs(new, initial)
                self.assertGreaterEqual(new.remaining, 0)

    def test_preview_stops_after_the_required_nonempty_lines(self):
        seen = []

        def lines():
            for line in ("\n", " A\n", " B\n"):
                seen.append(line)
                yield line

        self.assertEqual(self.module.first_nonempty(lines(), 0), ())
        self.assertEqual(seen, [])
        self.assertEqual(self.module.first_nonempty(lines(), 1), ("A",))
        self.assertEqual(seen, ["\n", " A\n"])

    def test_file_closes_on_exhaustion_early_exit_and_failures(self):
        with tempfile.TemporaryDirectory(prefix="functional-design-test-") as tmp:
            path = Path(tmp) / "lines.txt"
            path.write_text(" A\n B\n", encoding="utf-8")
            tracked = TrackingPath(path)
            self.assertEqual(self.module.read_preview(tracked, 1), ("A",))
            self.assertTrue(tracked.handles[-1].closed)
            self.assertEqual(self.module.read_preview(tracked, 9), ("A", "B"))
            self.assertTrue(tracked.handles[-1].closed)
            with self.assertRaises(ValueError):
                self.module.read_preview(tracked, -1)
            self.assertTrue(tracked.handles[-1].closed)
            path.write_bytes(b"\xff")
            with self.assertRaises(UnicodeDecodeError):
                self.module.read_preview(tracked, 1)
            self.assertTrue(all(handle.closed for handle in tracked.handles))


class DocumentationLinks(unittest.TestCase):
    def test_local_markdown_destinations_exist_inside_repository(self):
        for source in ROOT.rglob("*.md"):
            if ".git" in source.relative_to(ROOT).parts:
                continue
            text = source.read_text(encoding="utf-8")
            for target in re.findall(r"\]\(([^)]+)\)", text):
                if target.startswith(("https://", "http://", "mailto:")):
                    continue
                name, _, anchor = target.partition("#")
                destination = (source.parent / name).resolve() if name else source
                with self.subTest(source=source.relative_to(ROOT), target=target):
                    self.assertTrue(destination.is_relative_to(ROOT))
                    self.assertTrue(destination.is_file())
                    if anchor:
                        headings = re.findall(
                            r"^#+ (.+)$", destination.read_text(encoding="utf-8"), re.M
                        )
                        anchors = {
                            re.sub(r"[^\w\- ]", "", heading.lower()).replace(" ", "-")
                            for heading in headings
                        }
                        self.assertIn(anchor, anchors)


if __name__ == "__main__":
    unittest.main()
