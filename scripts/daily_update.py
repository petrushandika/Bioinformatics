#!/usr/bin/env python3
"""Update harian repo Bioinformatics.

Setiap run:
1. Mengambil topik kurikulum berikutnya yang masih `pending`.
2. Membuat materi (README.md) lewat 9Router Astronacci, plus `main.py` yang
   benar-benar dijalankan untuk topik berbasis kode.
3. Mengambil paper terbaru dari PubMed (fallback Europe PMC) dan merangkumnya.
4. Memperbarui Daily/, News/, kurikulum, dan README, lalu commit + push.

Hanya standard library. Topik baru ditandai selesai setelah materinya lolos validasi.
"""

from __future__ import annotations

import argparse
import ast
import json
import os
import re
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
CURRICULUM_FILE = ROOT / "scripts" / "curriculum.json"
DAILY_DIR = ROOT / "Daily"
NEWS_DIR = ROOT / "News"
SEEN_FILE = NEWS_DIR / "seen.json"
TZ = ZoneInfo("Asia/Jakarta")
USER_AGENT = "BioinformaticsLearningJournal/2.0 (+https://github.com/petrushandika/Bioinformatics)"

ROUTER_BASE_URL = os.environ.get("ROUTER_BASE_URL", "https://9router.ct.astronacci.co.id/v1").rstrip("/")
ROUTER_MODELS = [m.strip() for m in os.environ.get("ROUTER_MODELS", "cx/gpt-6.1-sol,cx/gpt-6-sol").split(",") if m.strip()]
CODE_CATEGORIES = {"Python", "Bioinformatics", "MachineLearning", "Mathematics"}
CATEGORY_LABELS = {
    "Biology": "🧬 Biologi",
    "Python": "💻 Python",
    "Mathematics": "📊 Matematika & Statistik",
    "Computing": "🖥️ Komputasi",
    "Bioinformatics": "🔬 Bioinformatika",
    "MachineLearning": "🤖 Machine Learning",
    "Capstone": "🎓 Capstone",
}
YEAR_LABELS = {1: "Tahun 1 — Fondasi", 2: "Tahun 2 — Konsep Inti", 3: "Tahun 3 — Spesialisasi", 4: "Tahun 4 — Aplikasi Lanjutan"}


class GenerationError(RuntimeError):
    pass


# ── HTTP ─────────────────────────────────────────────────────────────────────

def http_json(url: str, *, data: dict | None = None, headers: dict | None = None, timeout: int = 60, attempts: int = 3):
    body = json.dumps(data).encode() if data is not None else None
    hdrs = {"User-Agent": USER_AGENT, **(headers or {})}
    if body is not None:
        hdrs.setdefault("Content-Type", "application/json")
    last: Exception | None = None
    for attempt in range(attempts):
        try:
            req = urllib.request.Request(url, data=body, headers=hdrs, method="POST" if body else "GET")
            with urllib.request.urlopen(req, timeout=timeout) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            last = e
            if e.code not in (408, 409, 425, 429, 500, 502, 503, 504):
                raise
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            last = e
        time.sleep(5 * (attempt + 1))
    raise last  # type: ignore[misc]


# ── AI (9Router Astronacci) ──────────────────────────────────────────────────

def ai_generate(prompt: str, system: str, max_tokens: int = 8000) -> tuple[str, str]:
    key = os.environ.get("ROUTER_API_KEY", "")
    if not key:
        raise GenerationError("ROUTER_API_KEY belum diset di GitHub Secrets.")
    errors = []
    for model in ROUTER_MODELS:
        try:
            resp = http_json(
                f"{ROUTER_BASE_URL}/chat/completions",
                data={"model": model, "max_tokens": max_tokens, "messages": [
                    {"role": "system", "content": system}, {"role": "user", "content": prompt}]},
                headers={"Authorization": f"Bearer {key}"}, timeout=300,
            )
            text = (resp["choices"][0]["message"].get("content") or "").strip()
            if text:
                return text, model
            errors.append(f"{model}: respons kosong")
        except Exception as e:  # noqa: BLE001 - lanjut ke model cadangan
            errors.append(f"{model}: {getattr(e, 'code', '')} {type(e).__name__}")
        print(f"  ! {errors[-1]}")
    raise GenerationError("Semua model 9Router gagal: " + "; ".join(errors))


def strip_fence(text: str, lang: str = "") -> str:
    m = re.search(rf"```(?:{lang})?[^\n]*\n(.*?)```", text, flags=re.DOTALL)
    return (m.group(1) if m else text).strip() + "\n"


# ── Kurikulum ────────────────────────────────────────────────────────────────

def load_curriculum() -> dict:
    return json.loads(CURRICULUM_FILE.read_text(encoding="utf-8"))


def save_curriculum(data: dict) -> None:
    CURRICULUM_FILE.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def next_topic(data: dict) -> dict | None:
    return next((t for t in data["curriculum"] if t["status"] == "pending"), None)


def previous_topics(data: dict, topic: dict, n: int = 6) -> list[str]:
    done = [t["title"] for t in data["curriculum"] if t["status"] == "done"]
    return done[-n:]


SYSTEM_MATERI = (
    "Kamu adalah dosen bioinformatika yang menulis catatan belajar untuk pemula dalam Bahasa Indonesia. "
    "Tulis akurat secara ilmiah, terstruktur, dan konkret. Jangan mengarang referensi, angka, atau URL; "
    "jika menyebut sumber, gunakan hanya sumber umum yang pasti ada (mis. NCBI, UniProt, Ensembl, PDB, buku teks standar)."
)


def materi_prompt(topic: dict, recent: list[str]) -> str:
    code_note = (
        "Sertakan potongan kode Python singkat di dalam materi bila relevan. "
        if topic["category"] in CODE_CATEGORIES else
        "Sertakan contoh perintah/kode bila relevan untuk topik ini. " if topic["category"] == "Computing" else ""
    )
    return (
        f"Tulis materi belajar lengkap untuk topik: **{topic['title']}**\n"
        f"Kategori: {topic['category']} | Tahun kurikulum: {topic['year']}\n"
        f"Topik yang sudah dipelajari sebelumnya: {', '.join(recent) or '-'}\n\n"
        "Struktur wajib (Markdown):\n"
        f"# {topic['title']}\n"
        "## Tujuan Pembelajaran (3–5 poin)\n"
        "## Konsep Utama — beberapa subbagian ### dengan penjelasan mendalam\n"
        "## Tabel dan Diagram (minimal satu diagram bermakna dalam blok ```mermaid, bukan blok kosong; "
        "gunakan flowchart atau sequenceDiagram untuk menjelaskan hubungan/proses topik, bukan hiasan).\n"
        "Semua diagram/grafik wajib Mermaid. Dilarang diagram ASCII, kotak/anak panah teks, dan bar karakter. "
        "Tabel data tetap tabel Markdown; kode, output, sekuens, dan persamaan ilmiah tetap diperbolehkan.\n"
        "## Contoh Konkret\n"
        "## Hubungan dengan Bioinformatika\n"
        "## Ringkasan\n"
        "## Pertanyaan Latihan (5 soal bernomor)\n"
        "## Bacaan Lanjutan\n\n"
        f"{code_note}Panjang sekitar 1200–2000 kata. Keluarkan Markdown saja tanpa pembuka/penutup percakapan."
    )


REQUIRED_SECTIONS = ["Tujuan Pembelajaran", "Konsep Utama", "Contoh Konkret", "Hubungan dengan Bioinformatika", "Ringkasan", "Pertanyaan Latihan"]


def validate_materi(text: str) -> list[str]:
    problems = []
    if len(text) < 4000:
        problems.append(f"terlalu pendek ({len(text)} karakter)")
    for section in REQUIRED_SECTIONS:
        if not re.search(rf"^##\s+.*{re.escape(section)}", text, flags=re.MULTILINE | re.IGNORECASE):
            problems.append(f"bagian '{section}' tidak ada")
    fences = re.findall(r"^ {0,3}(`{3,}|~{3,})([^\n]*)\n(.*?)^ {0,3}\1[ \t]*$", text,
                        flags=re.MULTILINE | re.DOTALL)
    has_mermaid = False
    for _, language, body in fences:
        language = language.strip().lower()
        if language == "mermaid":
            # Lightweight content check, not a full Mermaid parser: a header alone is not a diagram.
            lines = [line.strip() for line in body.splitlines() if line.strip() and not line.lstrip().startswith("%%")]
            if (len(lines) >= 2 and re.match(
                    r"^(?:flowchart|graph|sequenceDiagram|pie|classDiagram|stateDiagram(?:-v2)?|erDiagram|"
                    r"journey|gantt|mindmap|timeline|quadrantChart|xychart-beta)\b", lines[0])):
                has_mermaid = True
        elif language in {"", "text", "plaintext", "ascii"}:
            # Target drawing structure, not ordinary output, alignment gaps, or equations such as A -> B.
            if re.search(r"[┌┐└┘├┤┬┴┼─│]|[█░▓▒]{2,}|\+[-=]{2,}\+|--+>|<--+|\|[-=]{2,}\|", body):
                problems.append("diagram ASCII/teks tidak diizinkan; gunakan Mermaid")
    if not has_mermaid:
        problems.append("diagram Mermaid bermakna dalam blok ```mermaid tidak ada")
    questions = re.search(r"##\s+Pertanyaan Latihan(.*?)(?:\n##\s|\Z)", text, flags=re.DOTALL | re.IGNORECASE)
    if questions and len(re.findall(r"^\s*\d+[.)]", questions.group(1), flags=re.MULTILINE)) < 5:
        problems.append("pertanyaan latihan kurang dari 5")
    return problems


def generate_materi(topic: dict, recent: list[str]) -> tuple[str, str]:
    prompt = materi_prompt(topic, recent)
    problems: list[str] = []
    for _ in range(2):
        text, model = ai_generate(prompt, SYSTEM_MATERI)
        text = strip_fence(text, "markdown") if text.lstrip().startswith("```") else text.strip() + "\n"
        problems = validate_materi(text)
        if not problems:
            return text, model
        print(f"  ! Materi belum valid ({'; '.join(problems)}), ulangi...")
        prompt = materi_prompt(topic, recent) + "\n\nPerbaiki kekurangan berikut: " + "; ".join(problems)
    raise GenerationError("Materi tidak lolos validasi: " + "; ".join(problems))


# ── Kode contoh (main.py) ────────────────────────────────────────────────────

FORBIDDEN_IMPORTS = {"os", "sys", "subprocess", "socket", "shutil", "urllib", "http", "requests", "ctypes", "pathlib", "importlib", "multiprocessing", "threading", "asyncio", "pickle", "signal"}
FORBIDDEN_CALLS = {"input", "open", "exec", "eval", "compile", "__import__", "breakpoint"}


def check_code_safety(code: str) -> list[str]:
    try:
        tree = ast.parse(code)
    except SyntaxError as e:
        return [f"syntax error: {e}"]
    problems = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else [node.module or ""]
            for name in names:
                if name.split(".")[0] in FORBIDDEN_IMPORTS:
                    problems.append(f"import '{name}' tidak diizinkan")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in FORBIDDEN_CALLS:
            problems.append(f"pemanggilan '{node.func.id}()' tidak diizinkan")
    return problems


def run_code(code: str, timeout: int = 30) -> tuple[bool, str]:
    with tempfile.TemporaryDirectory() as tmp:
        path = Path(tmp) / "main.py"
        path.write_text(code, encoding="utf-8")
        try:
            proc = subprocess.run([sys.executable, "-I", str(path)], cwd=tmp, env={"PATH": "/usr/bin:/bin"},
                                  stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout)
        except subprocess.TimeoutExpired:
            return False, "timeout"
    output = (proc.stdout + proc.stderr)[-3000:]
    return proc.returncode == 0 and bool(proc.stdout.strip()), output


CODE_SYSTEM = "Kamu menulis contoh kode Python edukatif yang bersih, berkomentar Bahasa Indonesia, dan bisa langsung dijalankan."


def generate_code(topic: dict, materi: str) -> tuple[str, str] | None:
    prompt = (
        f"Buat satu file `main.py` untuk topik '{topic['title']}' (kategori {topic['category']}).\n"
        "Aturan: hanya standard library Python 3.12 (tanpa numpy/pandas/biopython); tanpa input(), file, jaringan, "
        "os/sys/subprocess; data contoh ditulis langsung di kode (mis. sekuens DNA/protein pendek); harus selesai < 5 detik "
        "dan mencetak hasil yang menjelaskan dirinya. Gunakan fungsi dan `if __name__ == \"__main__\":`.\n"
        "Kembalikan hanya kode dalam satu blok ```python.\n\nRingkasan materi:\n" + materi[:3500]
    )
    for _ in range(2):
        try:
            raw, _model = ai_generate(prompt, CODE_SYSTEM, max_tokens=4000)
        except GenerationError as e:
            print(f"  ! Kode gagal dibuat: {e}")
            return None
        code = strip_fence(raw, "python")
        problems = check_code_safety(code)
        if not problems:
            ok, output = run_code(code)
            if ok:
                print("  ✓ main.py dijalankan dan berhasil")
                return code, output
            problems = [f"gagal dijalankan: {output[-800:]}"]
        print(f"  ! Kode belum valid: {problems[0][:200]}")
        prompt += "\n\nVersi sebelumnya bermasalah: " + "; ".join(problems)[:1500] + "\nPerbaiki."
    return None


# ── Paper ────────────────────────────────────────────────────────────────────

PAPER_QUERY = ('(bioinformatics[tiab] OR genomics[tiab] OR "computational biology"[tiab] OR transcriptomics[tiab] '
               'OR "protein structure"[tiab] OR "sequence alignment"[tiab]) AND hasabstract AND free full text[sb]')


def fetch_pubmed(today, limit: int = 12) -> list[dict]:
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
    params = {"db": "pubmed", "term": PAPER_QUERY, "retmode": "json", "retmax": limit, "sort": "pub_date",
              "datetype": "edat", "mindate": (today - timedelta(days=4)).strftime("%Y/%m/%d"), "maxdate": today.strftime("%Y/%m/%d")}
    ids = http_json(f"{base}/esearch.fcgi?{urllib.parse.urlencode(params)}", timeout=30)["esearchresult"]["idlist"]
    if not ids:
        return []
    time.sleep(1)
    summary = http_json(f"{base}/esummary.fcgi?{urllib.parse.urlencode({'db': 'pubmed', 'id': ','.join(ids), 'retmode': 'json'})}", timeout=30)["result"]
    time.sleep(1)
    req = urllib.request.Request(f"{base}/efetch.fcgi?{urllib.parse.urlencode({'db': 'pubmed', 'id': ','.join(ids), 'rettype': 'abstract', 'retmode': 'xml'})}",
                                 headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=60) as r:
        xml = r.read().decode("utf-8", "replace")
    abstracts = {}
    for article in re.findall(r"<PubmedArticle>(.*?)</PubmedArticle>", xml, flags=re.DOTALL):
        pmid = re.search(r"<PMID[^>]*>(\d+)</PMID>", article)
        parts = re.findall(r"<AbstractText[^>]*>(.*?)</AbstractText>", article, flags=re.DOTALL)
        if pmid:
            abstracts[pmid.group(1)] = re.sub(r"<[^>]+>", "", " ".join(parts)).strip()
    papers = []
    for pid in ids:
        s = summary.get(pid, {})
        authors = [a["name"] for a in s.get("authors", [])[:3]]
        doi = next((x["value"] for x in s.get("articleids", []) if x.get("idtype") == "doi"), "")
        papers.append({"id": f"pmid:{pid}", "title": re.sub(r"<[^>]+>", "", s.get("title", "")).strip(),
                       "authors": ", ".join(authors) + (" et al." if len(s.get("authors", [])) > 3 else ""),
                       "journal": s.get("fulljournalname") or s.get("source", ""), "year": (s.get("pubdate") or "")[:4],
                       "url": f"https://pubmed.ncbi.nlm.nih.gov/{pid}/", "doi": doi, "abstract": abstracts.get(pid, "")})
    return papers


def fetch_europepmc(today, limit: int = 12) -> list[dict]:
    q = (f'(bioinformatics OR genomics OR "computational biology") AND HAS_ABSTRACT:y AND OPEN_ACCESS:y '
         f'AND FIRST_PDATE:[{(today - timedelta(days=4)).isoformat()} TO {today.isoformat()}]')
    url = "https://www.ebi.ac.uk/europepmc/webservices/rest/search?" + urllib.parse.urlencode(
        {"query": q, "format": "json", "pageSize": limit, "resultType": "core"})
    papers = []
    for r in http_json(url, timeout=90, attempts=2).get("resultList", {}).get("result", []):
        papers.append({"id": f"epmc:{r.get('id')}", "title": (r.get("title") or "").strip(), "authors": r.get("authorString", "")[:120],
                       "journal": r.get("journalInfo", {}).get("journal", {}).get("title", ""), "year": str(r.get("pubYear", "")),
                       "url": f"https://doi.org/{r['doi']}" if r.get("doi") else f"https://europepmc.org/article/{r.get('source')}/{r.get('id')}",
                       "doi": r.get("doi", ""), "abstract": re.sub(r"<[^>]+>", "", r.get("abstractText", ""))})
    return papers


def collect_papers(today, seen: set[str], limit: int = 4) -> list[dict]:
    for source in (fetch_pubmed, fetch_europepmc):
        try:
            papers = [p for p in source(today) if p["title"] and len(p["abstract"]) > 200 and p["id"] not in seen]
            if papers:
                print(f"  {len(papers)} paper baru dari {source.__name__}")
                return papers[:limit]
        except Exception as e:  # noqa: BLE001
            print(f"  ! {source.__name__} gagal: {type(e).__name__} {e}")
    return []


def summarize_papers(papers: list[dict], recent: list[str]) -> tuple[str, str]:
    listing = "".join(f"\n### {i}. {p['title']}\nJurnal: {p['journal']} ({p['year']})\nAbstrak: {p['abstract'][:3500]}\n"
                      for i, p in enumerate(papers, 1))
    prompt = (f"Rangkum paper berikut untuk pembelajar bioinformatika pemula, dalam Bahasa Indonesia.\n{listing}\n\n"
              "Untuk tiap paper buat subjudul `### <nomor>. <judul singkat Indonesia>` lalu: 3–4 kalimat inti temuan "
              "(hanya dari abstrak, jangan menambah klaim), **Metode/teknologi**, dan **Kenapa penting**. "
              "Jika menggunakan chart/diagram, wajib blok mermaid, bukan ASCII atau gambar. Tabel tetap Markdown. "
              f"Tutup dengan `### Istilah Kunci` (5 istilah) dan `### Koneksi ke Kurikulum` (kaitkan dengan: {', '.join(recent) or 'dasar bioinformatika'}).")
    text, model = ai_generate(prompt, "Kamu mentor bioinformatika yang merangkum paper secara jujur dan ringkas.", max_tokens=4000)
    return text.strip() + "\n", model


# ── README ───────────────────────────────────────────────────────────────────

def topic_link(t: dict) -> str:
    return f"[{t['folder']}](./{t['folder']}/)" if t["status"] == "done" else f"`{t['folder']}/`"


def render_curriculum(data: dict) -> str:
    lines = ["<!-- CURRICULUM:START -->"]
    for year in sorted({t["year"] for t in data["curriculum"]}):
        lines += [f"### {YEAR_LABELS.get(year, f'Tahun {year}')}", "", "| Status | Kategori | Topik | Folder |", "|--------|----------|-------|--------|"]
        for t in (t for t in data["curriculum"] if t["year"] == year):
            lines.append(f"| {'✅' if t['status'] == 'done' else '🔜'} | {CATEGORY_LABELS.get(t['category'], t['category'])} | {t['title']} | {topic_link(t)} |")
        lines.append("")
    lines.append("<!-- CURRICULUM:END -->")
    return "\n".join(lines)


def render_progress(data: dict) -> str:
    counts: dict[str, list[int]] = {}
    for t in data["curriculum"]:
        c = counts.setdefault(t["category"], [0, 0])
        c[1] += 1
        c[0] += t["status"] == "done"
    rows = ["| Kategori | Tersedia | Total | Progress |", "|----------|---------|-------|----------|"]
    for cat, (done, total) in counts.items():
        rows.append(f"| {CATEGORY_LABELS.get(cat, cat)} | {done} | {total} | {round(done / total * 100)}% |")
    done = sum(c[0] for c in counts.values())
    total = sum(c[1] for c in counts.values())
    percent = round(done / total * 100) if total else 0
    rows.append(f"| **Total** | **{done}** | **{total}** | **{percent}%** |")
    diagram = (f'```mermaid\nflowchart LR\n    Total["Total: {total}"] --> Selesai["Tersedia: {done}"]\n'
               f'    Total --> Pending["Direncanakan: {total - done}"]\n```')
    return "<!-- PROGRESS:START -->\n" + diagram + "\n\n" + "\n".join(rows) + "\n<!-- PROGRESS:END -->"


def replace_block(text: str, heading: str, next_heading: str, block: str, marker: str) -> str:
    if f"<!-- {marker}:START -->" in text:
        return re.sub(rf"<!-- {marker}:START -->.*?<!-- {marker}:END -->", lambda _: block, text, flags=re.DOTALL)
    pattern = rf"(^## {re.escape(heading)}\n)(.*?)(?=^## {re.escape(next_heading)})"
    return re.sub(pattern, lambda m: m.group(1) + "\n" + block + "\n\n---\n\n", text, count=1, flags=re.DOTALL | re.MULTILINE)


def update_readme(data: dict) -> None:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")
    text = replace_block(text, "Kurikulum", "Progress Belajar", render_curriculum(data), "CURRICULUM")
    text = replace_block(text, "Progress Belajar", "Pembaruan Harian", render_progress(data), "PROGRESS")
    readme.write_text(text, encoding="utf-8")


# ── Tulis file & git ─────────────────────────────────────────────────────────

def paper_lines(papers: list[dict]) -> str:
    if not papers:
        return "_Tidak ada paper baru yang memenuhi kriteria hari ini._"
    return "\n".join(f"- [{p['title']}]({p['url']}) — {p['authors']} · *{p['journal']}, {p['year']}*" for p in papers)


def write_outputs(date_str: str, topic: dict | None, materi: str, code: tuple[str, str] | None, m_model: str,
                  papers: list[dict], news: str, n_model: str, created: list[tuple[dict, bool]] | None = None) -> None:
    DAILY_DIR.mkdir(exist_ok=True)
    (NEWS_DIR / "Archive").mkdir(parents=True, exist_ok=True)
    if topic:
        folder = ROOT / topic["folder"]
        folder.mkdir(parents=True, exist_ok=True)
        body = materi
        if code:
            body += f"\n---\n\n## Contoh Kode\n\nJalankan: `python {topic['folder']}/main.py`\n\n<details><summary>Contoh output</summary>\n\n```text\n{code[1].strip()[:2500]}\n```\n\n</details>\n"
            (folder / "main.py").write_text(code[0], encoding="utf-8")
        (folder / "README.md").write_text(body, encoding="utf-8")
    items = created if created else ([(topic, code is not None)] if topic else [])
    materi_section = ("## 📚 Materi Baru\n\n" + "\n".join(
        f"- [{t['title']}](../{t['folder']}/README.md) — {t['category']}, Tahun {t['year']}"
        + (" · `main.py` sudah dijalankan" if has_code else "") for t, has_code in items) + "\n"
        if items else "## 📚 Materi\n\n_Semua topik kurikulum sudah selesai._\n")
    digest = (f"# Update Harian — {date_str}\n\n> Dibuat otomatis via 9Router Astronacci · Materi: `{m_model}` · Rangkuman: `{n_model}`\n\n"
              f"{materi_section}\n---\n\n## 🔬 Paper Terbaru\n\n{paper_lines(papers)}\n\n### Rangkuman\n\n{news}\n")
    (DAILY_DIR / f"{date_str}.md").write_text(digest, encoding="utf-8")
    preview = re.sub(r"^#.*\n", "", materi, count=1).strip()[:600] if materi else ""
    (DAILY_DIR / "LATEST.md").write_text(
        f"# Update Terbaru — {date_str}\n\n" + (f"**Materi:** [{topic['title']}](../{topic['folder']}/README.md)\n\n{preview}…\n\n" if topic else "")
        + f"**Paper:** {len(papers)}\n\n[📖 Baca update lengkap](./{date_str}.md)\n", encoding="utf-8")
    (NEWS_DIR / "Archive" / f"{date_str}.md").write_text(
        f"# Berita Bioinformatika — {date_str}\n\n## Paper\n\n{paper_lines(papers)}\n\n---\n\n{news}\n", encoding="utf-8")
    (NEWS_DIR / "LATEST.md").write_text(
        f"# Berita Terbaru — {date_str}\n\n{paper_lines(papers)}\n\n[Rangkuman lengkap →](./Archive/{date_str}.md)\n", encoding="utf-8")


def git(*args: str) -> str:
    return subprocess.run(["git", *args], cwd=ROOT, check=True, capture_output=True, text=True).stdout


def commit_and_push(message: str, push: bool) -> bool:
    git("add", "-A")
    if subprocess.run(["git", "diff", "--cached", "--quiet"], cwd=ROOT).returncode == 0:
        print("Tidak ada perubahan.")
        return False
    git("-c", "user.name=github-actions[bot]", "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
        "commit", "-m", message)
    if push:
        for attempt in range(3):
            try:
                git("pull", "--rebase", "origin", "main")
                git("push", "origin", "HEAD:main")
                print("Push berhasil ✓")
                return True
            except subprocess.CalledProcessError as e:
                print(f"  ! push gagal ({attempt + 1}/3): {e.stderr.strip()[:300]}")
                time.sleep(10)
        raise RuntimeError("Push gagal setelah 3 percobaan")
    return True


# ── Main ─────────────────────────────────────────────────────────────────────

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--topics", type=int, default=int(os.environ.get("TOPICS_PER_RUN", "1") or 1))
    parser.add_argument("--force", action="store_true", help="tetap buat materi walau update hari ini sudah ada")
    parser.add_argument("--no-push", action="store_true")
    args = parser.parse_args()

    now = datetime.now(TZ)
    date_str = now.strftime("%Y-%m-%d")
    print(f"\n{'=' * 50}\nDAILY UPDATE {date_str} (WIB)\n{'=' * 50}")
    if (DAILY_DIR / f"{date_str}.md").exists() and not args.force:
        print("Update hari ini sudah ada — selesai tanpa perubahan.")
        return 0

    data = load_curriculum()
    created: list[tuple[dict, bool]] = []
    materi, code, m_model = "", None, "-"
    for _ in range(max(1, min(args.topics, 5))):
        topic = next_topic(data)
        if not topic:
            break
        print(f"\n[Materi] {topic['id']} — {topic['title']}")
        recent = previous_topics(data, topic)
        materi, m_model = generate_materi(topic, recent)
        code = generate_code(topic, materi) if topic["category"] in CODE_CATEGORIES else None
        topic["status"] = "done"
        write_outputs(date_str, topic, materi, code, m_model, [], "", "-")  # materi folder tersimpan dulu
        created.append((topic, code is not None))
    last_topic = created[-1][0] if created else None

    print("\n[Paper]")
    seen = set(json.loads(SEEN_FILE.read_text())) if SEEN_FILE.exists() else set()
    papers = collect_papers(now.date(), seen)
    news, n_model = "_Rangkuman tidak tersedia hari ini._", "-"
    if papers:
        try:
            news, n_model = summarize_papers(papers, [t["title"] for t, _ in created] or previous_topics(data, {}))
        except GenerationError as e:
            print(f"  ! Rangkuman gagal: {e}")
        SEEN_FILE.write_text(json.dumps(sorted(seen | {p["id"] for p in papers})[-1000:], indent=0) + "\n", encoding="utf-8")

    write_outputs(date_str, last_topic, materi, code, m_model, papers, news, n_model, created)
    save_curriculum(data)
    update_readme(data)
    titles = ", ".join(t["title"] for t, _ in created) or "Berita bioinformatika"
    commit_and_push(f"[Daily] {date_str}: {titles}", push=not args.no_push)
    print(f"\n✓ Selesai — materi: {titles} | paper: {len(papers)}")
    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except GenerationError as e:
        print(f"\n✗ GAGAL: {e}")
        sys.exit(1)
