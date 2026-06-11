#!/usr/bin/env python3
"""
news_update.py
Fetch paper terbaru dari Semantic Scholar API (tidak perlu auth, tidak rate-limit),
rangkum dengan AI gratis, commit ke GitHub.
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

from ai_client import generate

ROOT = Path(__file__).parent.parent
NEWS_DIR = ROOT / "News"
LATEST_NEWS = NEWS_DIR / "LATEST.md"
ARCHIVE_DIR = NEWS_DIR / "Archive"

SYSTEM = (
    "Kamu adalah mentor bioinformatika yang merangkum paper ilmiah menjadi mudah dipahami "
    "oleh mahasiswa pemula. Gunakan Bahasa Indonesia yang jelas dan sertakan konteks yang "
    "membantu memahami signifikansi penelitian."
)


# ── Semantic Scholar API ──────────────────────────────────────────────────────
# Tidak butuh API key, tidak ban GitHub Actions, gratis selamanya.

def _get_json(url: str, retries: int = 3) -> dict:
    headers = {"User-Agent": "bioinformatics-learning-journal/1.0"}
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.loads(r.read())
        except urllib.error.HTTPError as e:
            if e.code in (429, 503) and attempt < retries - 1:
                wait = 10 * (attempt + 1)
                print(f"  Rate limited ({e.code}), tunggu {wait}s...")
                time.sleep(wait)
            else:
                raise
    return {}


def fetch_papers(query: str, max_results: int = 3) -> list[dict]:
    """Ambil paper dari Semantic Scholar — tidak perlu auth."""
    params = urllib.parse.urlencode({
        "query": query,
        "limit": max_results,
        "fields": "title,abstract,authors,year,venue,externalIds,publicationDate,openAccessPdf",
        "sort": "publicationDate:desc",
    })
    url = f"https://api.semanticscholar.org/graph/v1/paper/search?{params}"
    data = _get_json(url)

    papers = []
    for item in data.get("data", []):
        authors = item.get("authors", [])
        author_str = ", ".join(a["name"] for a in authors[:3])
        if len(authors) > 3:
            author_str += " et al."

        ext = item.get("externalIds", {})
        pmid = ext.get("PubMed", "")
        doi  = ext.get("DOI", "")

        if doi:
            url_paper = f"https://doi.org/{doi}"
        elif pmid:
            url_paper = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        else:
            url_paper = f"https://www.semanticscholar.org/paper/{item.get('paperId','')}"

        pdf_url = ""
        if item.get("openAccessPdf"):
            pdf_url = item["openAccessPdf"].get("url", "")

        abstract = (item.get("abstract") or "Abstrak tidak tersedia.")[:600]

        papers.append({
            "title":    item.get("title") or "No title",
            "abstract": abstract,
            "authors":  author_str or "Unknown",
            "journal":  item.get("venue") or "Unknown Venue",
            "year":     str(item.get("year") or ""),
            "url":      url_paper,
            "pdf":      pdf_url,
        })
    return papers


# ── AI summarizer ─────────────────────────────────────────────────────────────

def summarize(papers: list[dict], date_str: str) -> tuple[str, str]:
    papers_text = "".join(
        f"\n### Paper {i}: {p['title']}\n"
        f"**Jurnal/Venue:** {p['journal']} ({p['year']}) | **Penulis:** {p['authors']}\n"
        f"**Abstrak:** {p['abstract']}\n"
        for i, p in enumerate(papers, 1)
    )
    prompt = (
        f"Berikut {len(papers)} paper bioinformatika terbaru ({date_str}):\n"
        f"{papers_text}\n\n"
        f"Buat rangkuman dalam Bahasa Indonesia:\n"
        f"1. Jelaskan setiap paper dalam 3–4 kalimat yang mudah dipahami pemula\n"
        f"2. Identifikasi teknologi/metode utama yang digunakan\n"
        f"3. Jelaskan mengapa paper ini penting untuk bioinformatika\n"
        f"4. Bagian **Istilah Kunci** — jelaskan 3–5 istilah teknis dari paper ini\n"
        f"5. Bagian **Koneksi ke Kurikulum** — topik belajar bioinformatika yang relevan\n\n"
        f"Format: Markdown rapi."
    )
    return generate(prompt, SYSTEM)


# ── File writing ──────────────────────────────────────────────────────────────

def write_files(papers: list[dict], summary: str, provider: str, date_str: str) -> list[Path]:
    NEWS_DIR.mkdir(exist_ok=True)
    ARCHIVE_DIR.mkdir(exist_ok=True)

    def paper_line(p: dict) -> str:
        line = f"- [{p['title']}]({p['url']}) — *{p['journal']}, {p['year']}*"
        if p["pdf"]:
            line += f" [[PDF]]({p['pdf']})"
        return line

    paper_list = "\n".join(paper_line(p) for p in papers)

    content = (
        f"# Update Bioinformatika Terbaru — {date_str}\n\n"
        f"> Sumber: [Semantic Scholar](https://www.semanticscholar.org/) | AI: {provider}\n\n"
        f"---\n\n"
        f"## Paper Hari Ini ({len(papers)} paper)\n\n"
        f"{paper_list}\n\n"
        f"---\n\n"
        f"## Rangkuman & Catatan Belajar\n\n"
        f"{summary}\n\n"
        f"---\n\n"
        f"_Sumber: Semantic Scholar | Dirangkum oleh AI ({provider})_\n"
    )

    archive = ARCHIVE_DIR / f"{date_str}.md"
    archive.write_text(content, encoding="utf-8")

    LATEST_NEWS.write_text(
        f"# Berita Bioinformatika Terbaru\n\n"
        f"**Diperbarui:** {date_str} | **AI:** {provider}\n\n"
        f"---\n\n"
        f"## Paper Hari Ini\n\n{paper_list}\n\n"
        f"---\n\n"
        + summary[:1000]
        + f"\n\n...\n\n[📖 Baca lengkap →](./Archive/{date_str}.md)\n",
        encoding="utf-8",
    )
    return [archive, LATEST_NEWS]


# ── Git ───────────────────────────────────────────────────────────────────────

def git_commit_and_push(date_str: str, files: list[Path]) -> None:
    def run(cmd):
        subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)

    run(["git", "config", "user.name", "github-actions[bot]"])
    run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
    for f in files:
        run(["git", "add", str(f.relative_to(ROOT))])
    run(["git", "commit", "-m", f"[News] {date_str}: Update berita bioinformatika terbaru"])
    run(["git", "push"])


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"=== News Update: {date_str} ===")

    all_papers, seen = [], set()
    queries = [
        "bioinformatics genomics",
        "protein structure prediction machine learning",
        "RNA sequencing transcriptomics",
    ]

    for i, q in enumerate(queries):
        if i > 0:
            time.sleep(2)
        print(f"Fetching: '{q}'...")
        for p in fetch_papers(q, max_results=2):
            key = p["title"]
            if key not in seen:
                seen.add(key)
                all_papers.append(p)
        if len(all_papers) >= 5:
            break

    papers = all_papers[:5]
    if not papers:
        print("Tidak ada paper ditemukan.")
        sys.exit(0)

    print(f"{len(papers)} paper ditemukan. Merangkum via AI...")
    summary, provider = summarize(papers, date_str)

    files = write_files(papers, summary, provider, date_str)
    git_commit_and_push(date_str, files)
    print(f"Selesai! {len(papers)} paper dirangkum via {provider}.")


if __name__ == "__main__":
    main()
