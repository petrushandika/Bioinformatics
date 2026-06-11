#!/usr/bin/env python3
"""
news_update.py
Setiap hari: cari paper/berita bioinformatika terbaru via PubMed API,
lalu minta Claude merangkum dan membuat catatan belajar, kemudian commit ke GitHub.
"""

import json
import os
import sys
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, timedelta
from pathlib import Path
import subprocess
import anthropic

ROOT = Path(__file__).parent.parent
NEWS_DIR = ROOT / "News"
LATEST_NEWS = NEWS_DIR / "LATEST.md"
ARCHIVE_DIR = NEWS_DIR / "Archive"


# ── PubMed fetch ──────────────────────────────────────────────────────────────

def fetch_pubmed_papers(query: str = "bioinformatics", max_results: int = 5) -> list[dict]:
    """Ambil paper terbaru dari PubMed API."""
    base = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/"

    # Cari ID paper
    yesterday = (datetime.now(timezone.utc) - timedelta(days=7)).strftime("%Y/%m/%d")
    search_params = urllib.parse.urlencode({
        "db": "pubmed",
        "term": f"{query}[Title/Abstract] AND {yesterday}[PDAT]:3000[PDAT]",
        "retmax": max_results,
        "sort": "pub+date",
        "retmode": "json",
    })
    with urllib.request.urlopen(f"{base}esearch.fcgi?{search_params}") as resp:
        search_data = json.loads(resp.read())

    ids = search_data.get("esearchresult", {}).get("idlist", [])
    if not ids:
        # fallback: ambil paper terbaru tanpa filter tanggal
        search_params = urllib.parse.urlencode({
            "db": "pubmed",
            "term": f"{query}[Title/Abstract]",
            "retmax": max_results,
            "sort": "pub+date",
            "retmode": "json",
        })
        with urllib.request.urlopen(f"{base}esearch.fcgi?{search_params}") as resp:
            search_data = json.loads(resp.read())
        ids = search_data.get("esearchresult", {}).get("idlist", [])

    if not ids:
        return []

    # Fetch detail
    fetch_params = urllib.parse.urlencode({
        "db": "pubmed",
        "id": ",".join(ids),
        "retmode": "xml",
    })
    with urllib.request.urlopen(f"{base}efetch.fcgi?{fetch_params}") as resp:
        xml_data = resp.read()

    root = ET.fromstring(xml_data)
    papers = []
    for article in root.findall(".//PubmedArticle"):
        title_el = article.find(".//ArticleTitle")
        abstract_el = article.find(".//AbstractText")
        pmid_el = article.find(".//PMID")
        journal_el = article.find(".//Journal/Title")
        year_el = article.find(".//PubDate/Year")
        authors = article.findall(".//Author/LastName")

        title = title_el.text if title_el is not None else "No title"
        abstract = abstract_el.text if abstract_el is not None else "No abstract available"
        pmid = pmid_el.text if pmid_el is not None else ""
        journal = journal_el.text if journal_el is not None else "Unknown Journal"
        year = year_el.text if year_el is not None else "2024"
        author_list = ", ".join(a.text for a in authors[:3] if a.text)
        if len(authors) > 3:
            author_list += " et al."

        papers.append({
            "title": title,
            "abstract": abstract[:600],
            "pmid": pmid,
            "journal": journal,
            "year": year,
            "authors": author_list,
            "url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        })

    return papers


# ── Claude summarizer ─────────────────────────────────────────────────────────

def summarize_with_claude(papers: list[dict], date_str: str) -> str:
    """Minta Claude merangkum paper dan membuat catatan belajar."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    papers_text = ""
    for i, p in enumerate(papers, 1):
        papers_text += (
            f"\n### Paper {i}: {p['title']}\n"
            f"**Jurnal:** {p['journal']} ({p['year']})\n"
            f"**Penulis:** {p['authors']}\n"
            f"**PMID:** {p['pmid']}\n"
            f"**Abstrak:** {p['abstract']}\n"
        )

    prompt = (
        f"Berikut adalah {len(papers)} paper bioinformatika terbaru dari PubMed ({date_str}):\n"
        f"{papers_text}\n\n"
        f"Tolong buat rangkuman dalam Bahasa Indonesia yang:\n"
        f"1. Menjelaskan setiap paper dalam 3–4 kalimat yang mudah dipahami pemula\n"
        f"2. Mengidentifikasi teknologi/metode utama yang digunakan\n"
        f"3. Menjelaskan mengapa paper ini penting untuk bioinformatika\n"
        f"4. Menambahkan bagian 'Istilah Kunci' yang menjelaskan istilah teknis baru\n"
        f"5. Menambahkan 'Koneksi ke Kurikulum' — topik mana dalam belajar bioinformatika yang relevan\n\n"
        f"Format: Markdown yang rapi dan terstruktur."
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=3000,
        messages=[{"role": "user", "content": prompt}],
        system=(
            "Kamu adalah mentor bioinformatika yang membuat ringkasan paper ilmiah "
            "menjadi mudah dipahami oleh mahasiswa pemula. Gunakan Bahasa Indonesia yang jelas "
            "dan sertakan konteks yang membantu memahami signifikansi penelitian."
        ),
    )
    return message.content[0].text


# ── File writing ──────────────────────────────────────────────────────────────

def write_news_files(papers: list[dict], summary: str, date_str: str) -> list[Path]:
    NEWS_DIR.mkdir(exist_ok=True)
    ARCHIVE_DIR.mkdir(exist_ok=True)

    # Paper list section
    paper_list = "\n".join(
        f"- [{p['title']}]({p['url']}) — *{p['journal']}, {p['year']}*"
        for p in papers
    )

    header = (
        f"# Update Bioinformatika Terbaru — {date_str}\n\n"
        f"> Diperbarui otomatis setiap hari dari PubMed\n\n"
        f"---\n\n"
        f"## Paper Hari Ini ({len(papers)} paper)\n\n"
        f"{paper_list}\n\n"
        f"---\n\n"
        f"## Rangkuman & Catatan Belajar\n\n"
        f"{summary}\n\n"
        f"---\n\n"
        f"_Sumber: [PubMed](https://pubmed.ncbi.nlm.nih.gov/) | Dirangkum oleh Claude AI_\n"
    )

    # Arsip harian
    archive_file = ARCHIVE_DIR / f"{date_str}.md"
    archive_file.write_text(header, encoding="utf-8")

    # Update LATEST.md
    latest = (
        f"# Berita Bioinformatika Terbaru\n\n"
        f"**Diperbarui:** {date_str}\n\n"
        f"---\n\n"
        f"## Paper Hari Ini\n\n"
        f"{paper_list}\n\n"
        f"---\n\n"
        f"## Ringkasan\n\n"
        + summary[:1000]
        + "\n\n...\n\n"
        f"[📖 Baca lengkap →](./Archive/{date_str}.md)\n"
    )
    LATEST_NEWS.write_text(latest, encoding="utf-8")

    return [archive_file, LATEST_NEWS]


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

    queries = [
        "bioinformatics machine learning",
        "genomics sequencing analysis",
        "protein structure prediction",
    ]

    all_papers = []
    for q in queries:
        print(f"Fetching PubMed: '{q}'...")
        papers = fetch_pubmed_papers(q, max_results=2)
        all_papers.extend(papers)
        if len(all_papers) >= 5:
            break

    # Deduplicate by PMID
    seen = set()
    unique_papers = []
    for p in all_papers:
        if p["pmid"] not in seen:
            seen.add(p["pmid"])
            unique_papers.append(p)

    unique_papers = unique_papers[:5]

    if not unique_papers:
        print("Tidak ada paper ditemukan hari ini.")
        sys.exit(0)

    print(f"Ditemukan {len(unique_papers)} paper. Merangkum dengan Claude...")
    summary = summarize_with_claude(unique_papers, date_str)

    print("Menulis file...")
    files = write_news_files(unique_papers, summary, date_str)

    print("Committing ke GitHub...")
    git_commit_and_push(date_str, files)

    print(f"Selesai! {len(unique_papers)} paper dirangkum dan dipush.")


if __name__ == "__main__":
    main()
