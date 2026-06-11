#!/usr/bin/env python3
"""
news_update.py
Fetch paper terbaru dari PubMed, rangkum dengan AI gratis, commit ke GitHub.
"""

import json
import os
import sys
import time
import urllib.request
import urllib.error
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path
import subprocess

from ai_client import generate

ROOT = Path(__file__).parent.parent
NEWS_DIR = ROOT / "News"
LATEST_NEWS = NEWS_DIR / "LATEST.md"
ARCHIVE_DIR = NEWS_DIR / "Archive"

# PubMed memerlukan email & tool agar tidak di-rate-limit
PUBMED_EMAIL = "petrushandikasinaga@gmail.com"
PUBMED_TOOL  = "bioinformatics-learning-journal"

SYSTEM = (
    "Kamu adalah mentor bioinformatika yang merangkum paper ilmiah menjadi mudah dipahami "
    "oleh mahasiswa pemula. Gunakan Bahasa Indonesia yang jelas dan sertakan konteks yang "
    "membantu memahami signifikansi penelitian."
)


def _pubmed_get(url: str, retries: int = 3) -> bytes:
    """GET dengan retry + backoff untuk menghindari 429."""
    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": PUBMED_TOOL})
            with urllib.request.urlopen(req, timeout=30) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 429 and attempt < retries - 1:
                wait = 5 * (attempt + 1)   # 5s, 10s, 15s
                print(f"  Rate limited, tunggu {wait}s...")
                time.sleep(wait)
            else:
                raise
    return b""


def fetch_pubmed_papers(query: str, max_results: int = 3) -> list[dict]:
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"
    common = {"email": PUBMED_EMAIL, "tool": PUBMED_TOOL}
    week_ago = (datetime.now(timezone.utc) - timedelta(days=30)).strftime("%Y/%m/%d")

    # Coba dengan filter tanggal, fallback tanpa filter
    ids: list[str] = []
    for term in [
        f"{query}[Title/Abstract] AND {week_ago}[PDAT]:3000[PDAT]",
        f"{query}[Title/Abstract]",
    ]:
        params = urllib.parse.urlencode({**common,
            "db": "pubmed", "term": term,
            "retmax": max_results, "sort": "pub+date", "retmode": "json",
        })
        data = _pubmed_get(f"{base}esearch.fcgi?{params}")
        ids = json.loads(data).get("esearchresult", {}).get("idlist", [])
        if ids:
            break
        time.sleep(1)   # jeda antar request

    if not ids:
        return []

    time.sleep(1)   # jeda sebelum efetch
    params = urllib.parse.urlencode({**common,
        "db": "pubmed", "id": ",".join(ids), "retmode": "xml",
    })
    xml_data = _pubmed_get(f"{base}efetch.fcgi?{params}")
    root = ET.fromstring(xml_data)

    papers = []
    for article in root.findall(".//PubmedArticle"):
        def txt(path):
            el = article.find(path)
            return el.text if el is not None else ""

        authors = article.findall(".//Author/LastName")
        author_str = ", ".join(a.text for a in authors[:3] if a.text)
        if len(authors) > 3:
            author_str += " et al."

        pmid = txt(".//PMID")
        papers.append({
            "title":    txt(".//ArticleTitle") or "No title",
            "abstract": (txt(".//AbstractText") or "")[:600],
            "pmid":     pmid,
            "journal":  txt(".//Journal/Title") or "Unknown Journal",
            "year":     txt(".//PubDate/Year") or "2024",
            "authors":  author_str,
            "url":      f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        })
    return papers


def summarize(papers: list[dict], date_str: str) -> tuple[str, str]:
    papers_text = "".join(
        f"\n### Paper {i}: {p['title']}\n"
        f"**Jurnal:** {p['journal']} ({p['year']}) | **Penulis:** {p['authors']}\n"
        f"**Abstrak:** {p['abstract']}\n"
        for i, p in enumerate(papers, 1)
    )
    prompt = (
        f"Berikut {len(papers)} paper bioinformatika terbaru dari PubMed ({date_str}):\n"
        f"{papers_text}\n\n"
        f"Buat rangkuman Bahasa Indonesia:\n"
        f"1. Jelaskan setiap paper dalam 3–4 kalimat untuk pemula\n"
        f"2. Identifikasi teknologi/metode utama\n"
        f"3. Jelaskan mengapa paper ini penting\n"
        f"4. Bagian 'Istilah Kunci' — jelaskan istilah teknis baru\n"
        f"5. Bagian 'Koneksi ke Kurikulum' — topik belajar yang relevan\n\n"
        f"Format: Markdown rapi."
    )
    return generate(prompt, SYSTEM)


def write_files(papers: list[dict], summary: str, provider: str, date_str: str) -> list[Path]:
    NEWS_DIR.mkdir(exist_ok=True)
    ARCHIVE_DIR.mkdir(exist_ok=True)

    paper_list = "\n".join(
        f"- [{p['title']}]({p['url']}) — *{p['journal']}, {p['year']}*"
        for p in papers
    )
    content = (
        f"# Update Bioinformatika Terbaru — {date_str}\n\n"
        f"> Sumber: PubMed NCBI | AI Provider: {provider}\n\n"
        f"---\n\n"
        f"## Paper Hari Ini ({len(papers)} paper)\n\n"
        f"{paper_list}\n\n"
        f"---\n\n"
        f"## Rangkuman & Catatan Belajar\n\n"
        f"{summary}\n\n"
        f"---\n\n"
        f"_[PubMed](https://pubmed.ncbi.nlm.nih.gov/) | Dirangkum oleh AI ({provider})_\n"
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


def git_commit_and_push(date_str: str, files: list[Path]) -> None:
    def run(cmd):
        subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)

    run(["git", "config", "user.name", "github-actions[bot]"])
    run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
    for f in files:
        run(["git", "add", str(f.relative_to(ROOT))])
    run(["git", "commit", "-m", f"[News] {date_str}: Update berita bioinformatika terbaru"])
    run(["git", "push"])


def main() -> None:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"=== News Update: {date_str} ===")

    all_papers, seen = [], set()
    queries = ["bioinformatics", "genomics sequencing", "protein structure prediction"]
    for i, q in enumerate(queries):
        if i > 0:
            time.sleep(3)   # jeda 3 detik antar query agar tidak kena rate limit
        print(f"Fetching: '{q}'...")
        for p in fetch_pubmed_papers(q, max_results=2):
            if p["pmid"] not in seen:
                seen.add(p["pmid"])
                all_papers.append(p)
        if len(all_papers) >= 5:
            break

    papers = all_papers[:5]
    if not papers:
        print("Tidak ada paper hari ini.")
        sys.exit(0)

    print(f"{len(papers)} paper ditemukan. Merangkum...")
    summary, provider = summarize(papers, date_str)

    files = write_files(papers, summary, provider, date_str)
    git_commit_and_push(date_str, files)
    print(f"Selesai! {len(papers)} paper dirangkum via {provider}.")


if __name__ == "__main__":
    main()
