#!/usr/bin/env python3
"""
daily_update.py — Master script update harian.

Yang dilakukan setiap hari:
  1. Generate 1 materi kurikulum baru (Biology / Python / Math / Bioinformatics)
  2. Fetch paper terbaru dari Semantic Scholar + rangkum dengan AI
  3. Tulis Daily/<tanggal>.md berisi KEDUANYA sekaligus
  4. Update News/LATEST.md
  5. Update README.md progress bar
  6. Commit & push semua sekaligus
"""

import json
import os
import re
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
import subprocess
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from ai_client import generate

# ── Paths ─────────────────────────────────────────────────────────────────────
ROOT            = Path(__file__).parent.parent
CURRICULUM_FILE = Path(__file__).parent / "curriculum.json"
DAILY_DIR       = ROOT / "Daily"
NEWS_DIR        = ROOT / "News"
NEWS_LATEST     = NEWS_DIR / "LATEST.md"
NEWS_ARCHIVE    = NEWS_DIR / "Archive"

# ── Prompts ───────────────────────────────────────────────────────────────────
SYSTEM_MATERI = (
    "Kamu adalah pengajar bioinformatika yang menulis materi belajar dalam Bahasa Indonesia. "
    "Buat konten markdown komprehensif, terstruktur, mudah dipahami pemula. "
    "Gunakan contoh nyata, diagram ASCII, dan tabel. "
    "Akhiri dengan '## Pertanyaan Latihan' (5 soal) dan '## Relevansi dengan Bioinformatika'."
)

SYSTEM_NEWS = (
    "Kamu adalah mentor bioinformatika yang merangkum paper ilmiah menjadi mudah dipahami "
    "mahasiswa pemula. Gunakan Bahasa Indonesia yang jelas."
)


# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 1: KURIKULUM
# ══════════════════════════════════════════════════════════════════════════════

def load_curriculum() -> dict:
    with open(CURRICULUM_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_curriculum(data: dict) -> None:
    with open(CURRICULUM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_next_topic(data: dict) -> dict | None:
    for t in data["curriculum"]:
        if t["status"] == "pending":
            return t
    return None


def mark_done(data: dict, topic_id: str) -> None:
    for t in data["curriculum"]:
        if t["id"] == topic_id:
            t["status"] = "done"
            break


def generate_materi(topic: dict) -> tuple[str, str]:
    prompt = (
        f"Buat materi pembelajaran lengkap dalam Bahasa Indonesia:\n\n"
        f"**Topik: {topic['title']}**\n"
        f"Kategori: {topic['category']} | Tahun: {topic['year']}\n\n"
        f"Wajib ada:\n"
        f"1. Definisi dan konsep utama\n"
        f"2. Sub-topik dengan penjelasan mendalam\n"
        f"3. Tabel perbandingan atau diagram ASCII\n"
        f"4. Contoh konkret dan kode (jika relevan)\n"
        f"5. Hubungan langsung dengan bioinformatika\n"
        f"6. 5 pertanyaan latihan\n\n"
        f"Format: Markdown murni, siap jadi README.md."
    )
    return generate(prompt, SYSTEM_MATERI)


def update_readme_progress(data: dict) -> None:
    readme = ROOT / "README.md"
    if not readme.exists():
        return
    text = readme.read_text(encoding="utf-8")

    counts: dict[str, dict] = {}
    for t in data["curriculum"]:
        cat = t["category"]
        counts.setdefault(cat, {"done": 0, "total": 0})
        counts[cat]["total"] += 1
        if t["status"] == "done":
            counts[cat]["done"] += 1

    def bar(done: int, total: int, w: int = 10) -> str:
        filled = round((done / total) * w) if total else 0
        pct    = round((done / total) * 100) if total else 0
        return f"{'█' * filled}{'░' * (w - filled)}  {pct:3d}%"

    def c(cat):
        return counts.get(cat, {"done": 0, "total": 1})

    new_block = (
        "```\n"
        f"Biologi         {bar(c('Biology')['done'],        c('Biology')['total'])}\n"
        f"Python          {bar(c('Python')['done'],         c('Python')['total'])}\n"
        f"Matematika      {bar(c('Mathematics')['done'],    c('Mathematics')['total'])}\n"
        f"Bioinformatika  {bar(c('Bioinformatics')['done'], c('Bioinformatics')['total'])}\n"
        f"Machine Learning{bar(c('MachineLearning')['done'],c('MachineLearning')['total'])}\n"
        "```"
    )
    new_text = re.sub(r"```\nBiologi.*?```", new_block, text, flags=re.DOTALL)
    readme.write_text(new_text, encoding="utf-8")


# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 2: PAPER / BERITA
# ══════════════════════════════════════════════════════════════════════════════

def _http_get(url: str) -> dict:
    headers = {"User-Agent": "BioinformaticsLearningJournal/1.0"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def fetch_papers(query: str, limit: int = 2) -> list[dict]:
    params = urllib.parse.urlencode({
        "query": query,
        "limit": limit,
        "fields": "title,abstract,authors,year,venue,externalIds,openAccessPdf",
    })
    data = _http_get(
        f"https://api.semanticscholar.org/graph/v1/paper/search?{params}"
    )
    papers = []
    for item in data.get("data", []):
        authors = item.get("authors") or []
        author_str = ", ".join(a.get("name", "") for a in authors[:3])
        if len(authors) > 3:
            author_str += " et al."

        ext  = item.get("externalIds") or {}
        doi  = ext.get("DOI", "")
        pmid = ext.get("PubMed", "")
        pid  = item.get("paperId", "")
        link = (f"https://doi.org/{doi}" if doi else
                f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else
                f"https://www.semanticscholar.org/paper/{pid}")

        pdf = (item.get("openAccessPdf") or {}).get("url", "")

        papers.append({
            "title":    (item.get("title") or "No title").strip(),
            "abstract": ((item.get("abstract") or "Abstrak tidak tersedia."))[:500],
            "authors":  author_str or "Unknown",
            "journal":  item.get("venue") or "Unknown Venue",
            "year":     str(item.get("year") or ""),
            "url":      link,
            "pdf":      pdf,
        })
    return papers


def collect_papers() -> list[dict]:
    queries = [
        "bioinformatics genomics 2024",
        "protein structure prediction deep learning",
        "single cell RNA sequencing analysis",
    ]
    seen, result = set(), []
    for i, q in enumerate(queries):
        if i:
            time.sleep(2)
        try:
            print(f"  Fetching papers: '{q}'...")
            for p in fetch_papers(q):
                if p["title"] not in seen:
                    seen.add(p["title"])
                    result.append(p)
        except Exception as e:
            print(f"  Skip '{q}': {e}")
        if len(result) >= 5:
            break
    return result[:5]


def summarize_papers(papers: list[dict], date_str: str) -> tuple[str, str]:
    papers_text = "".join(
        f"\n### Paper {i}: {p['title']}\n"
        f"**Venue:** {p['journal']} ({p['year']}) | **Penulis:** {p['authors']}\n"
        f"**Abstrak:** {p['abstract']}\n"
        for i, p in enumerate(papers, 1)
    )
    prompt = (
        f"Berikut {len(papers)} paper bioinformatika terbaru ({date_str}):\n"
        f"{papers_text}\n\n"
        f"Buat rangkuman Bahasa Indonesia:\n"
        f"1. Jelaskan setiap paper dalam 3-4 kalimat untuk pemula\n"
        f"2. Teknologi/metode utama yang digunakan\n"
        f"3. Mengapa paper ini penting\n"
        f"4. **Istilah Kunci** — 3-5 istilah teknis\n"
        f"5. **Koneksi ke Kurikulum** — topik belajar yang relevan\n\n"
        f"Format: Markdown."
    )
    return generate(prompt, SYSTEM_NEWS)


def summarize_no_papers(date_str: str) -> tuple[str, str]:
    prompt = (
        f"Buat update bioinformatika harian ({date_str}) dalam Bahasa Indonesia:\n"
        f"1. Pilih 1 topik bioinformatika yang sedang trending\n"
        f"2. Jelaskan konsep tersebut untuk pemula (3-4 paragraf)\n"
        f"3. Mengapa topik ini penting saat ini\n"
        f"4. **Istilah Kunci** — 5 istilah teknis\n"
        f"5. **Sumber Belajar** — cara mempelajari lebih lanjut\n\n"
        f"Format: Markdown."
    )
    return generate(prompt, SYSTEM_NEWS)


# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 3: TULIS FILE
# ══════════════════════════════════════════════════════════════════════════════

def write_daily_digest(
    date_str: str,
    topic: dict | None,
    materi: str,
    materi_provider: str,
    papers: list[dict],
    news_summary: str,
    news_provider: str,
) -> Path:
    """Tulis satu file harian yang berisi materi + berita sekaligus."""
    DAILY_DIR.mkdir(exist_ok=True)

    # ── bagian materi ──
    if topic:
        materi_section = (
            f"## 📚 Materi Hari Ini: {topic['title']}\n\n"
            f"> Kategori: **{topic['category']}** | Tahun Kurikulum: **{topic['year']}**  \n"
            f"> File lengkap: [{topic['folder']}/README.md](../{topic['folder']}/README.md)  \n"
            f"> AI Provider: {materi_provider}\n\n"
            f"{materi}\n"
        )
    else:
        materi_section = "## 📚 Materi Hari Ini\n\n_Semua topik kurikulum sudah selesai!_\n"

    # ── bagian paper ──
    if papers:
        def pline(p):
            s = f"- [{p['title']}]({p['url']}) — *{p['journal']}, {p['year']}*"
            if p["pdf"]:
                s += f" [[PDF]]({p['pdf']})"
            return s
        paper_list = "\n".join(pline(p) for p in papers)
    else:
        paper_list = "_Tidak ada paper hari ini (API tidak tersedia)._"

    news_section = (
        f"## 🔬 Paper Bioinformatika Terbaru\n\n"
        f"{paper_list}\n\n"
        f"### Rangkuman\n\n"
        f"{news_summary}\n"
    )

    content = (
        f"# Update Harian Bioinformatika — {date_str}\n\n"
        f"> Diperbarui otomatis oleh GitHub Actions\n\n"
        f"---\n\n"
        f"{materi_section}\n"
        f"---\n\n"
        f"{news_section}\n"
        f"---\n\n"
        f"_AI Materi: {materi_provider} | AI Berita: {news_provider}_\n"
    )

    path = DAILY_DIR / f"{date_str}.md"
    path.write_text(content, encoding="utf-8")

    # Update LATEST.md (ringkasan singkat)
    latest_content = (
        f"# Update Terbaru — {date_str}\n\n"
        + (f"**Materi:** [{topic['title']}](../{topic['folder']}/README.md)  \n"
           f"**Kategori:** {topic['category']}\n\n" if topic else "")
        + f"**Paper hari ini:** {len(papers)} paper\n\n"
        f"---\n\n"
        f"📖 [Baca update lengkap hari ini](./{date_str}.md)\n\n"
        f"### Cuplikan Materi\n\n"
        + materi[:600] + "\n\n...\n\n"
        f"### Cuplikan Berita\n\n"
        + news_summary[:400] + "\n\n...\n\n"
        f"[→ Baca selengkapnya](./{date_str}.md)\n"
    )
    (DAILY_DIR / "LATEST.md").write_text(latest_content, encoding="utf-8")

    return path


def write_news_files(
    date_str: str, papers: list[dict], summary: str, provider: str
) -> list[Path]:
    NEWS_DIR.mkdir(exist_ok=True)
    NEWS_ARCHIVE.mkdir(exist_ok=True)

    if papers:
        def pline(p):
            s = f"- [{p['title']}]({p['url']}) — *{p['journal']}, {p['year']}*"
            if p["pdf"]:
                s += f" [[PDF]]({p['pdf']})"
            return s
        paper_list = "\n".join(pline(p) for p in papers)
    else:
        paper_list = "_Tidak ada paper hari ini._"

    full = (
        f"# Berita Bioinformatika — {date_str}\n\n"
        f"> Sumber: Semantic Scholar | AI: {provider}\n\n---\n\n"
        f"## Paper ({len(papers)})\n\n{paper_list}\n\n---\n\n"
        f"## Rangkuman\n\n{summary}\n\n---\n\n"
        f"_Dirangkum oleh AI ({provider})_\n"
    )
    arc = NEWS_ARCHIVE / f"{date_str}.md"
    arc.write_text(full, encoding="utf-8")

    NEWS_LATEST.write_text(
        f"# Berita Bioinformatika Terbaru\n\n"
        f"**Diperbarui:** {date_str} | **AI:** {provider}\n\n---\n\n"
        f"## Paper\n\n{paper_list}\n\n---\n\n"
        + summary[:1000]
        + f"\n\n...\n\n[📖 Lengkap →](./Archive/{date_str}.md)\n",
        encoding="utf-8",
    )
    return [arc, NEWS_LATEST]


# ══════════════════════════════════════════════════════════════════════════════
# BAGIAN 4: GIT
# ══════════════════════════════════════════════════════════════════════════════

def git_push(date_str: str, all_files: list[Path], topic: dict | None) -> None:
    def run(cmd):
        subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)

    run(["git", "config", "user.name",  "github-actions[bot]"])
    run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])

    for f in all_files:
        if f.exists():
            run(["git", "add", str(f.relative_to(ROOT))])

    run(["git", "add", "README.md", "scripts/curriculum.json"])

    # Cek ada perubahan
    check = subprocess.run(
        ["git", "diff", "--cached", "--quiet"], cwd=ROOT, capture_output=True
    )
    if check.returncode == 0:
        print("Tidak ada perubahan baru.")
        return

    label = topic["title"] if topic else "Semua selesai"
    run(["git", "commit", "-m", f"[Daily] {date_str}: {label}"])
    run(["git", "push"])
    print("Push berhasil.")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main() -> None:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"\n{'='*50}")
    print(f"DAILY UPDATE: {date_str}")
    print(f"{'='*50}\n")

    all_files: list[Path] = []

    # ── 1. Materi kurikulum ───────────────────────────────────────────────────
    print("[ 1/3 ] Generate materi kurikulum...")
    data    = load_curriculum()
    topic   = get_next_topic(data)
    materi  = ""
    materi_provider = "N/A"
    topic_readme: Path | None = None

    if topic:
        print(f"  Topik: {topic['title']} ({topic['category']})")
        try:
            materi, materi_provider = generate_materi(topic)
            topic_dir    = ROOT / topic["folder"]
            topic_dir.mkdir(parents=True, exist_ok=True)
            topic_readme = topic_dir / "README.md"
            topic_readme.write_text(materi, encoding="utf-8")
            all_files.append(topic_readme)
            mark_done(data, topic["id"])
            save_curriculum(data)
            update_readme_progress(data)
            print(f"  Selesai via {materi_provider}")
        except Exception as e:
            print(f"  Gagal generate materi: {e}")
            topic = None
    else:
        print("  Semua topik kurikulum sudah selesai!")

    # ── 2. Paper & berita ─────────────────────────────────────────────────────
    print("\n[ 2/3 ] Fetch & rangkum paper terbaru...")
    papers = []
    try:
        papers = collect_papers()
        print(f"  {len(papers)} paper ditemukan.")
    except Exception as e:
        print(f"  Fetch gagal: {e} — pakai mode fallback.")

    news_summary   = ""
    news_provider  = "N/A"
    try:
        if papers:
            news_summary, news_provider = summarize_papers(papers, date_str)
        else:
            news_summary, news_provider = summarize_no_papers(date_str)
        print(f"  Rangkuman selesai via {news_provider}")
    except Exception as e:
        print(f"  Gagal rangkum: {e}")
        news_summary = "_Gagal mengambil rangkuman hari ini._"

    news_files = write_news_files(date_str, papers, news_summary, news_provider)
    all_files.extend(news_files)

    # ── 3. Tulis daily digest ─────────────────────────────────────────────────
    print("\n[ 3/3 ] Tulis daily digest & push...")
    daily_file = write_daily_digest(
        date_str, topic, materi, materi_provider,
        papers, news_summary, news_provider,
    )
    all_files.append(daily_file)
    all_files.append(DAILY_DIR / "LATEST.md")

    git_push(date_str, all_files, topic)

    print(f"\n✓ Update {date_str} selesai!")
    if topic:
        print(f"  Materi : {topic['title']}")
    print(f"  Paper  : {len(papers)} paper")
    print(f"  Files  : {len(all_files)} file diperbarui")


if __name__ == "__main__":
    main()
