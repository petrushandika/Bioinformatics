"""Offline regression tests for generated learning documentation."""
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch


SPEC = importlib.util.spec_from_file_location(
    "daily_update", Path(__file__).resolve().parents[1] / "scripts" / "daily_update.py"
)
assert SPEC is not None and SPEC.loader is not None
daily = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(daily)


class ProgressTests(unittest.TestCase):
    def test_counts_and_empty_curriculum(self):
        cases = [
            ([], ["| **Total** | **0** | **0** | **0%** |"], 0, 0),
            ([{"category": "Biology", "status": "done"},
              {"category": "Biology", "status": "pending"},
              {"category": "Python", "status": "done"}],
             ["| 🧬 Biologi | 1 | 2 | 50% |", "| 💻 Python | 1 | 1 | 100% |",
              "| **Total** | **2** | **3** | **67%** |"], 2, 1),
            ([{"category": "Python", "status": "done"}],
             ["| 💻 Python | 1 | 1 | 100% |"], 1, 0),
            ([{"category": "Python", "status": "pending"}],
             ["| 💻 Python | 0 | 1 | 0% |"], 0, 1),
        ]
        for topics, rows, done, pending in cases:
            with self.subTest(topics=topics):
                result = daily.render_progress({"curriculum": topics})
                self.assertIn("```mermaid\nflowchart LR", result)
                self.assertIn(f'Selesai["Tersedia: {done}"]', result)
                self.assertIn(f'Pending["Direncanakan: {pending}"]', result)
                for row in rows:
                    self.assertIn(row, result)
                self.assertNotIn("█", result)
                self.assertNotIn("░", result)


def materi(extra=""):
    sections = "\n".join(f"## {name}\nPenjelasan.\n" for name in daily.REQUIRED_SECTIONS)
    return "# Materi\n" + sections + "\n1. A\n2. B\n3. C\n4. D\n5. E\n" + ("Penjelasan ilmiah. " * 250) + "\n" + extra


MERMAID = '```mermaid\nflowchart LR\n    A[DNA] --> B[RNA]\n```\n'


class MateriTests(unittest.TestCase):
    def test_requires_meaningful_mermaid_not_just_table_or_code(self):
        for extra in ("", "| A | B |\n|---|---|", "```python\nprint(1)\n```",
                      "```mermaid\n```", "```mermaid\nflowchart LR\n%% comment\n```"):
            with self.subTest(extra=extra):
                self.assertTrue(any("Mermaid" in p for p in daily.validate_materi(materi(extra))))
        self.assertEqual([], daily.validate_materi(materi(MERMAID)))

    def test_prompt_requires_mermaid_and_forbids_ascii(self):
        prompt = daily.materi_prompt({"title": "DNA", "category": "Biology", "year": 1}, [])
        self.assertIn("```mermaid", prompt)
        self.assertIn("Dilarang", prompt)
        self.assertNotIn("atau diagram ASCII", prompt)

    def test_rejects_ascii_diagrams_but_allows_code_output_sequences_and_equations(self):
        diagrams = ["+-----+\n| DNA |\n+-----+", "[DNA] --> [RNA]", "├── DNA\n└── RNA", "DNA ███░░"]
        for diagram in diagrams:
            for language in ("", "text", "plaintext", "ascii"):
                with self.subTest(diagram=diagram, language=language):
                    problems = daily.validate_materi(materi(MERMAID + f"```{language}\n{diagram}\n```"))
                    self.assertTrue(any("ASCII" in p for p in problems), problems)
        legitimate = ["```python\nprint('[DNA] --> [RNA]')\n```",
                      "```text\nGC content: 50%\ncount = 4\n```", "```\nACGT--ACGT\nAC-TGGACGT\n```",
                      "```text\n>seq1\nACGTACGT\n```", "```text\nv = k * [A] * [B]\nA + B -> C\n```",
                      "| A | B |\n|---|---|\n| 1 | 2 |"]
        for extra in legitimate:
            with self.subTest(extra=extra):
                self.assertEqual([], daily.validate_materi(materi(MERMAID + extra)))


class ReadmeTests(unittest.TestCase):
    def test_markers_surrounding_content_and_idempotence(self):
        topic = {"category": "Biology", "status": "done", "year": 1, "folder": "Biology/DNA", "title": "DNA"}
        for use_markers in (False, True):
            with self.subTest(use_markers=use_markers), tempfile.TemporaryDirectory() as tmp:
                path = Path(tmp) / "README.md"
                curriculum = "<!-- CURRICULUM:START -->\nold\n<!-- CURRICULUM:END -->" if use_markers else "old curriculum"
                progress = "<!-- PROGRESS:START -->\nold\n<!-- PROGRESS:END -->" if use_markers else "old progress"
                path.write_text(f"# Intro\n\n## Kurikulum\n\n{curriculum}\n\n## Progress Belajar\n\n{progress}\n\n## Pembaruan Harian\nKeep me.\n", encoding="utf-8")
                with patch.object(daily, "ROOT", Path(tmp)):
                    daily.update_readme({"curriculum": [topic]})
                    once = path.read_text(encoding="utf-8")
                    daily.update_readme({"curriculum": [topic]})
                self.assertEqual(once, path.read_text(encoding="utf-8"))
                self.assertTrue(once.startswith("# Intro\n"))
                self.assertTrue(once.endswith("## Pembaruan Harian\nKeep me.\n"))
                for marker in ("CURRICULUM", "PROGRESS"):
                    self.assertEqual(1, once.count(f"<!-- {marker}:START -->"))
                    self.assertEqual(1, once.count(f"<!-- {marker}:END -->"))
                self.assertIn(MERMAID.splitlines()[0], once)
                self.assertNotIn("\nold\n", once)
                self.assertNotIn("old curriculum", once)
                self.assertNotIn("old progress", once)


if __name__ == "__main__":
    unittest.main()
