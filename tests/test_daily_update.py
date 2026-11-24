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
                self.assertIn("```mermaid\nflowchart TD", result)
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


class NormalizationTests(unittest.TestCase):
    def test_math_and_summary_headings_preserve_fenced_content_and_are_idempotent(self):
        protected = ("```python\n" + r'print("\\(x\\)")' + "\n### Istilah Kunci\n```\n"
                     + "~~~~mermaid\nflowchart TD\n" + r'A["\\[x\\]"] --> B' + "\n```\n~~~~\n")
        raw = (r"Inline \(x + y\) dan \\(z\\)." + "\n" + r"\[a=b\]" + "\n"
               + r"\\[c=d\\]" + "\n" + protected
               + "### Istilah Kunci\nGen.\n### Koneksi ke Kurikulum\nDNA.\n")
        result = daily.normalize_markdown(raw, news=True)
        self.assertIn("Inline $x + y$ dan $z$.", result)
        self.assertIn("$$\na=b\n$$", result)
        self.assertIn("$$\nc=d\n$$", result)
        self.assertIn(protected, result)
        self.assertIn("\n## Istilah Kunci\n", result)
        self.assertIn("\n## Koneksi ke Kurikulum\n", result)
        self.assertEqual(result, daily.normalize_markdown(result, news=True))

    def test_fake_generation_preserves_inner_fences_and_normalizes_math(self):
        topic = {"title": "DNA", "category": "Biology", "year": 1}
        source = materi(MERMAID + r"Inline \\(x\\)." + "\n```python\nprint('safe')\n```\n")
        for raw in (source, "```markdown\n" + source + "```", "````markdown\n" + source + "````"):
            with self.subTest(wrapper=raw[:15]), \
                    patch.object(daily, "ai_generate", return_value=(raw, "fake")), \
                    patch.object(daily.urllib.request, "urlopen", side_effect=AssertionError("network forbidden")):
                result, model = daily.generate_materi(topic, [])
                self.assertEqual("fake", model)
                self.assertIn(MERMAID, result)
                self.assertIn("```python\nprint('safe')\n```", result)
                self.assertIn("Inline $x$.", result)
                self.assertEqual([], daily.validate_materi(result))
        # A code fence at the start is content, not a Markdown response wrapper.
        self.assertEqual(MERMAID, daily.normalize_markdown(MERMAID))

    def test_prompts_use_clean_headings_github_math_and_vertical_diagrams(self):
        prompt = daily.materi_prompt({"title": "DNA", "category": "Biology", "year": 1}, [])
        self.assertIn("$...$", prompt)
        self.assertIn("$$...$$", prompt)
        self.assertIn("flowchart TD", prompt)
        for line in prompt.splitlines():
            if line.startswith("## "):
                self.assertNotIn("(", line)
                self.assertNotIn("—", line)


class OutputTests(unittest.TestCase):
    def test_code_output_cannot_close_its_display_fence(self):
        topic = {"title": "DNA", "folder": "Biology/DNA", "category": "Biology", "year": 1}
        output = "before\n```\n## Not a heading\nafter"
        with tempfile.TemporaryDirectory() as tmp, patch.object(daily, "ROOT", Path(tmp)), \
                patch.object(daily, "DAILY_DIR", Path(tmp) / "Daily"), \
                patch.object(daily, "NEWS_DIR", Path(tmp) / "News"), \
                patch.object(daily.urllib.request, "urlopen", side_effect=AssertionError("network forbidden")):
            daily.write_outputs("2026-01-01", topic, "# DNA\n", ("print('ok')\n", output),
                                "fake", [], "_Tidak ada rangkuman._", "-")
            lesson = (Path(tmp) / topic["folder"] / "README.md").read_text()
            self.assertIn("````text\n" + output + "\n````", lesson)
            self.assertEqual("print('ok')\n", (Path(tmp) / topic["folder"] / "main.py").read_text())
            self.assertIn("Tidak ada paper baru", (Path(tmp) / "News/LATEST.md").read_text())

    def test_outputs_use_summary_links_metadata_and_sibling_navigation(self):
        topics = [{"title": title, "folder": f"Biology/{title}", "category": "Biology", "year": 1}
                  for title in ("DNA", "RNA")]
        papers = [{"title": "Paper title", "url": "https://example.org/paper", "authors": "Author",
                   "journal": "Journal", "year": "2026"}]
        news = "### 1. Temuan\n\nIsi.\n\n### Istilah Kunci\n\nGen.\n\n### Koneksi ke Kurikulum\n\nDNA.\n"
        with tempfile.TemporaryDirectory() as tmp, patch.object(daily, "ROOT", Path(tmp)), \
                patch.object(daily, "DAILY_DIR", Path(tmp) / "Daily"), \
                patch.object(daily, "NEWS_DIR", Path(tmp) / "News"), \
                patch.object(daily.urllib.request, "urlopen", side_effect=AssertionError("network forbidden")):
            for created in ([(t, False) for t in topics], []):
                with self.subTest(created=created):
                    daily.write_outputs("2026-01-01", topics[-1] if created else None,
                                        "# RNA\n\n```python\n" + "source-preview" * 100,
                                        None, "fake", papers, news, "fake", created)
                    latest = (Path(tmp) / "Daily/LATEST.md").read_text()
                    self.assertNotIn("source-preview", latest)
                    self.assertNotIn("```", latest)
                    for topic, _ in created:
                        self.assertIn(f"[{topic['title']}](../{topic['folder']}/README.md)", latest)
                    if not created:
                        self.assertIn("Semua topik kurikulum sudah selesai", latest)
                    for relative, home, counterpart in (
                        ("Daily/2026-01-01.md", "../README.md", "../News/Archive/2026-01-01.md"),
                        ("Daily/LATEST.md", "../README.md", "../News/LATEST.md"),
                        ("News/Archive/2026-01-01.md", "../../README.md", "../../Daily/2026-01-01.md"),
                        ("News/LATEST.md", "../README.md", "../Daily/LATEST.md"),
                    ):
                        text = (Path(tmp) / relative).read_text()
                        self.assertIn(f"]({home})", text)
                        self.assertIn(f"]({counterpart})", text)
                        if "LATEST" not in relative:
                            self.assertIn("## Rangkuman\n\n### 1. Temuan", text)
                            self.assertIn("\n## Istilah Kunci\n", text)
                            self.assertIn("\n## Koneksi ke Kurikulum\n", text)
                    self.assertIn("- [Paper title](https://example.org/paper)\n  - Author · *Journal, 2026*",
                                  (Path(tmp) / "News/LATEST.md").read_text())


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


class ProseBoundaryTests(unittest.TestCase):
    def test_inline_and_nested_code_preserved(self):
        source = 'Use `re.compile(r"\\(x\\)")` then \\(y\\).'
        self.assertEqual(daily.normalize_markdown(source), 'Use `re.compile(r"\\(x\\)")` then $y$.\n')
        source = '1. Example\n\n    ```python\n    print(r"\\(x\\)")\n    ```\n'
        self.assertEqual(daily.normalize_markdown(source), source)
        self.assertEqual(daily.normalize_markdown(r"Equation: \[x=1\] then continue."), 'Equation: \n\n$$\nx=1\n$$\n\n then continue.\n')


class EscapedMathTests(unittest.TestCase):
    def test_doubled_commands_and_single_delimiter_rowbreaks(self):
        self.assertEqual(daily.normalize_markdown(r"\\(V_{\\max}\\)"), "$V_{\\max}$\n")
        self.assertEqual(daily.normalize_markdown(r"\[a \\ b\]"), "$$\na \\\\ b\n$$\n")


if __name__ == "__main__":
    unittest.main()
