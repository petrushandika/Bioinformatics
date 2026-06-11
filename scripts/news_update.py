#!/usr/bin/env python3
"""
news_update.py — Fetch paper bioinformatika terbaru + rangkum dengan AI.
Sumber: Semantic Scholar (tanpa auth, tidak kena rate-limit di GitHub Actions).
Jika fetch gagal, AI tetap generate topik bioinformatika terbaru tanpa paper nyata.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
import subprocess

sys.path.insert(0, str(Path(__file__).parent))
from ai_client import generate

ROOT      = Path(__file__).parent.parent
NEWS_DIR  = ROOT / "News"
LATEST    = NEWS_DIR / "LATEST.md"
ARCHIVE   = NEWS_DIR / "Archive"

SYSTEM = (
    "Kamu adalah mentor bioinformatika yang merangkum paper ilmiah menjadi mudah dipahami "
    "oleh mahasiswa pemula. Gunakan Bahasa Indonesia yang jelas dan sertakan konteks yang "
    "membantu memahami signifikansi penelitian."
)


# ── Fetch dari Semantic Scholar ───────────────────────────────────────────────

def _http_get(url: str) -> dict:
    headers = {"User-Agent": "BioinformaticsLearningJournal/1.0 (educational project)"}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def fetch_papers(query: str, limit: int = 3) -> list[dict]:
    params = urllib.parse.urlencode({
        "query": query,
        "limit": limit,
        "fields": "title,abstract,authors,year,venue,externalIds,openAccessPdf",
    })
    data = _http_get(f"https://api.semanticscholar.org/graph/v1/paper/search?{params}")

    papers = []
    for item in data.get("data", []):
        authors = item.get("authors") or []
        author_str = ", ".join(a.get("name", "") for a in authors[:3])
        if len(authors) > 3:
            author_str += " et al."

        ext = item.get("externalIds") or {}
        doi  = ext.get("DOI", "")
        pmid = ext.get("PubMed", "")
        pid  = item.get("paperId", "")

        link = (f"https://doi.org/{doi}" if doi else
                f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else
                f"https://www.semanticscholar.org/paper/{pid}")

        pdf = ""
        if item.get("openAccessPdf"):
            pdf = item["openAccessPdf"].get("url", "")

        papers.append({
            "title":    (item.get("title") or "No title").strip(),
            "abstract": ((item.get("abstract") or "") or "Abstrak tidak tersedia.")[:600],
            "authors":  author_str or "Unknown",
            "journal":  item.get("venue") or "Unknown Venue",
            "year":     str(item.get("year") or ""),
            "url":      link,
            "pdf":      pdf,
        })
    return papers


def collect_papers() -> list[dict]:
    """Coba beberapa query, return gabungan unik hingga 5 paper."""
    queries = [
        "bioinformatics genomics 2024",
        "protein structure prediction deep learning",
        "RNA sequencing single cell",
    ]
    seen, all_papers = set(), []
    for i, q in enumerate(queries):
        if i:
            time.sleep(2)
        try:
            print(f"  Fetching: '{q}'...")
            for p in fetch_papers(q, limit=2):
                if p["title"] not in seen:
                    seen.add(p["title"])
                    all_papers.append(p)
        except Exception as e:
            print(f"  Fetch gagal untuk '{q}': {e}")
        if len(all_papers) >= 5:
            break
    return all_papers[:5]


# ── AI summarize ──────────────────────────────────────────────────────────────

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
        f"Buat rangkuman dalam Bahasa Indonesia:\n"
        f"1. Jelaskan setiap paper dalam 3-4 kalimat untuk pemula\n"
        f"2. Identifikasi metode/teknologi utama yang digunakan\n"
        f"3. Jelaskan mengapa paper ini penting\n"
        f"4. **Istilah Kunci** — jelaskan 3-5 istilah teknis dari paper ini\n"
        f"5. **Koneksi ke Kurikulum** — topik belajar bioinformatika yang relevan\n\n"
        f"Format: Markdown rapi."
    )
    return generate(prompt, SYSTEM)


def generate_without_papers(date_str: str) -> tuple[str, str]:
    """Fallback: AI buat konten bioinformatika tanpa paper nyata."""
    prompt = (
        f"Hari ini ({date_str}) tidak ada paper yang berhasil diambil dari API. "
        f"Tolong buat update harian bioinformatika dalam Bahasa Indonesia yang mencakup:\n"
        f"1. Satu topik bioinformatika terkini yang sedang ramai dibahas\n"
        f"2. Penjelasan konsep tersebut untuk pemula\n"
        f"3. Mengapa topik ini penting saat ini\n"
        f"4. **Istilah Kunci** — 5 istilah teknis yang relevan\n"
        f"5. **Sumber Belajar** — cara mempelajari lebih lanjut\n\n"
        f"Format: Markdown rapi."
    )
    return generate(prompt, SYSTEM)


# ── Tulis file ────────────────────────────────────────────────────────────────

def write_files(papers: list[dict], summary: str, provider: str, date_str: str) -> list[Path]:
    NEWS_DIR.mkdir(exist_ok=True)
    ARCHIVE.mkdir(exist_ok=True)

    if papers:
        def line(p):
            s = f"- [{p['title']}]({p['url']}) — *{p['journal']}, {p['year']}*"
            if p["pdf"]:
                s += f" [[PDF]]({p['pdf']})"
            return s
        paper_list = "\n".join(line(p) for p in papers)
        source_note = f"Sumber: [Semantic Scholar](https://www.semanticscholar.org/) | AI: {provider}"
    else:
        paper_list  = "_Tidak ada paper hari ini — konten dibuat langsung oleh AI._"
        source_note = f"AI: {provider} (mode fallback)"

    full = (
        f"# Update Bioinformatika — {date_str}\n\n"
        f"> {source_note}\n\n---\n\n"
        f"## Paper Hari Ini\n\n{paper_list}\n\n---\n\n"
        f"## Rangkuman & Catatan Belajar\n\n{summary}\n\n---\n\n"
        f"_Dirangkum oleh AI ({provider})_\n"
    )

    arc = ARCHIVE / f"{date_str}.md"
    arc.write_text(full, encoding="utf-8")

    LATEST.write_text(
        f"# Berita Bioinformatika Terbaru\n\n"
        f"**Diperbarui:** {date_str} | **AI:** {provider}\n\n---\n\n"
        f"## Paper Hari Ini\n\n{paper_list}\n\n---\n\n"
        + summary[:1000]
        + f"\n\n...\n\n[📖 Baca lengkap →](./Archive/{date_str}.md)\n",
        encoding="utf-8",
    )
    return [arc, LATEST]


# ── Git ───────────────────────────────────────────────────────────────────────

def git_push(date_str: str, files: list[Path]) -> None:
    def run(cmd):
        subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)

    run(["git", "config", "user.name",  "github-actions[bot]"])
    run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
    for f in files:
        run(["git", "add", str(f.relative_to(ROOT))])

    # Cek apakah ada perubahan sebelum commit
    result = subprocess.run(
        ["git", "diff", "--cached", "--quiet"],
        cwd=ROOT, capture_output=True
    )
    if result.returncode == 0:
        print("Tidak ada perubahan untuk di-commit.")
        return

    run(["git", "commit", "-m", f"[News] {date_str}: Update bioinformatika terbaru"])
    run(["git", "push"])


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"=== News Update: {date_str} ===")

    # 1. Ambil paper (tidak crash jika gagal)
    papers = []
    try:
        papers = collect_papers()
        print(f"{len(papers)} paper ditemukan.")
    except Exception as e:
        print(f"Fetch paper gagal total: {e} — lanjut dengan mode fallback.")

    # 2. Generate summary via AI
    try:
        if papers:
            summary, provider = summarize_papers(papers, date_str)
        else:
            summary, provider = generate_without_papers(date_str)
    except Exception as e:
        print(f"AI generation gagal: {e}")
        sys.exit(1)

    # 3. Tulis file & push
    files = write_files(papers, summary, provider, date_str)
    git_push(date_str, files)
    print(f"Selesai! Provider: {provider}")


if __name__ == "__main__":
    main()
