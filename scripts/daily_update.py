#!/usr/bin/env python3
"""
daily_update.py
Satu-satunya script update harian. Tidak ada import file lain.
Jalankan: python scripts/daily_update.py
"""

import json
import os
import re
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT            = Path(__file__).resolve().parent.parent
CURRICULUM_FILE = Path(__file__).resolve().parent / "curriculum.json"
DAILY_DIR       = ROOT / "Daily"
NEWS_DIR        = ROOT / "News"

# ══════════════════════════════════════════════════════════════════════════════
# AI — Groq utama, Mistral fallback
# ══════════════════════════════════════════════════════════════════════════════

def _post(url: str, headers: dict, body: dict) -> dict:
    raw = json.dumps(body).encode()
    req = urllib.request.Request(url, data=raw, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read())


def ai_generate(prompt: str, system: str) -> tuple[str, str]:
    """Return (teks, provider). Coba Groq dulu, fallback Mistral."""

    groq_key    = os.environ.get("GROQ_API_KEY", "")
    mistral_key = os.environ.get("MISTRAL_API_KEY", "")

    if not groq_key and not mistral_key:
        raise RuntimeError(
            "Tidak ada API key!\n"
            "Tambahkan GROQ_API_KEY atau MISTRAL_API_KEY di GitHub Secrets.\n"
            "Groq gratis: https://console.groq.com\n"
            "Mistral gratis: https://console.mistral.ai"
        )

    providers = []
    if groq_key:
        providers.append(("Groq", lambda: _post(
            "https://api.groq.com/openai/v1/chat/completions",
            {"Authorization": f"Bearer {groq_key}", "Content-Type": "application/json"},
            {"model": "llama3-70b-8192",
             "messages": [{"role": "system", "content": system},
                          {"role": "user",   "content": prompt}],
             "max_tokens": 4096},
        )["choices"][0]["message"]["content"]))

    if mistral_key:
        providers.append(("Mistral", lambda: _post(
            "https://api.mistral.ai/v1/chat/completions",
            {"Authorization": f"Bearer {mistral_key}", "Content-Type": "application/json"},
            {"model": "mistral-small-latest",
             "messages": [{"role": "system", "content": system},
                          {"role": "user",   "content": prompt}],
             "max_tokens": 4096},
        )["choices"][0]["message"]["content"]))

    last_err = None
    for name, call in providers:
        try:
            print(f"  AI: {name}...")
            return call(), name
        except Exception as e:
            print(f"  {name} gagal: {e}")
            last_err = e

    raise RuntimeError(f"Semua provider gagal: {last_err}")


# ══════════════════════════════════════════════════════════════════════════════
# KURIKULUM — generate materi harian
# ══════════════════════════════════════════════════════════════════════════════

SYSTEM_MATERI = (
    "Kamu adalah pengajar bioinformatika. Tulis materi belajar dalam Bahasa Indonesia "
    "yang komprehensif, terstruktur, dan mudah dipahami pemula. "
    "Gunakan contoh nyata, diagram ASCII, dan tabel. "
    "Akhiri dengan '## Pertanyaan Latihan' (5 soal) dan '## Relevansi dengan Bioinformatika'."
)


def load_curriculum() -> dict:
    with open(CURRICULUM_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_curriculum(data: dict) -> None:
    with open(CURRICULUM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def next_topic(data: dict) -> dict | None:
    return next((t for t in data["curriculum"] if t["status"] == "pending"), None)


def mark_done(data: dict, tid: str) -> None:
    for t in data["curriculum"]:
        if t["id"] == tid:
            t["status"] = "done"
            break


def update_progress(data: dict) -> None:
    readme = ROOT / "README.md"
    if not readme.exists():
        return
    counts: dict[str, dict] = {}
    for t in data["curriculum"]:
        c = counts.setdefault(t["category"], {"done": 0, "total": 0})
        c["total"] += 1
        if t["status"] == "done":
            c["done"] += 1

    def bar(d, total, w=10):
        f = round(d / total * w) if total else 0
        return f"{'█'*f}{'░'*(w-f)}  {round(d/total*100) if total else 0:3d}%"

    def g(cat):
        return counts.get(cat, {"done": 0, "total": 1})

    block = (
        "```\n"
        f"Biologi         {bar(g('Biology')['done'],        g('Biology')['total'])}\n"
        f"Python          {bar(g('Python')['done'],         g('Python')['total'])}\n"
        f"Matematika      {bar(g('Mathematics')['done'],    g('Mathematics')['total'])}\n"
        f"Bioinformatika  {bar(g('Bioinformatics')['done'], g('Bioinformatics')['total'])}\n"
        f"Machine Learning{bar(g('MachineLearning')['done'],g('MachineLearning')['total'])}\n"
        "```"
    )
    text = re.sub(r"```\nBiologi.*?```", block, readme.read_text(encoding="utf-8"), flags=re.DOTALL)
    readme.write_text(text, encoding="utf-8")


# ══════════════════════════════════════════════════════════════════════════════
# PAPER — Semantic Scholar (tanpa auth, aman di GitHub Actions)
# ══════════════════════════════════════════════════════════════════════════════

SYSTEM_NEWS = (
    "Kamu adalah mentor bioinformatika. Rangkum paper ilmiah dalam Bahasa Indonesia "
    "yang mudah dipahami pemula. Sertakan istilah kunci dan koneksi ke kurikulum belajar."
)


def fetch_papers(query: str, limit: int = 2) -> list[dict]:
    params = urllib.parse.urlencode({
        "query": query, "limit": limit,
        "fields": "title,abstract,authors,year,venue,externalIds,openAccessPdf",
    })
    req = urllib.request.Request(
        f"https://api.semanticscholar.org/graph/v1/paper/search?{params}",
        headers={"User-Agent": "BioinformaticsLearningJournal/1.0"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        data = json.loads(r.read())

    papers = []
    for item in data.get("data", []):
        authors = item.get("authors") or []
        astr = ", ".join(a.get("name", "") for a in authors[:3])
        if len(authors) > 3:
            astr += " et al."
        ext  = item.get("externalIds") or {}
        doi  = ext.get("DOI", "")
        pmid = ext.get("PubMed", "")
        pid  = item.get("paperId", "")
        url  = (f"https://doi.org/{doi}" if doi else
                f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/" if pmid else
                f"https://www.semanticscholar.org/paper/{pid}")
        pdf  = (item.get("openAccessPdf") or {}).get("url", "")
        papers.append({
            "title":    (item.get("title") or "").strip(),
            "abstract": (item.get("abstract") or "Abstrak tidak tersedia.")[:500],
            "authors":  astr or "Unknown",
            "journal":  item.get("venue") or "Unknown",
            "year":     str(item.get("year") or ""),
            "url":      url,
            "pdf":      pdf,
        })
    return papers


def collect_papers() -> list[dict]:
    queries = [
        "bioinformatics genomics 2024",
        "protein structure prediction deep learning",
        "single cell RNA sequencing",
    ]
    seen, result = set(), []
    for i, q in enumerate(queries):
        if i:
            time.sleep(2)
        try:
            print(f"  Fetch papers: '{q}'")
            for p in fetch_papers(q):
                if p["title"] and p["title"] not in seen:
                    seen.add(p["title"])
                    result.append(p)
        except Exception as e:
            print(f"  Skip '{q}': {e}")
        if len(result) >= 5:
            break
    return result[:5]


# ══════════════════════════════════════════════════════════════════════════════
# TULIS FILE
# ══════════════════════════════════════════════════════════════════════════════

def write_all(date_str, topic, materi, m_prov, papers, news, n_prov) -> list[Path]:
    files: list[Path] = []
    DAILY_DIR.mkdir(exist_ok=True)
    NEWS_DIR.mkdir(exist_ok=True)
    (NEWS_DIR / "Archive").mkdir(exist_ok=True)

    # ── materi folder (Biology/Python/dll) ──────────────────────────────────
    if topic and materi:
        d = ROOT / topic["folder"]
        d.mkdir(parents=True, exist_ok=True)
        f = d / "README.md"
        f.write_text(materi, encoding="utf-8")
        files.append(f)
        print(f"  Ditulis: {f.relative_to(ROOT)}")

    # ── daily digest ────────────────────────────────────────────────────────
    def pline(p):
        s = f"- [{p['title']}]({p['url']}) — *{p['journal']}, {p['year']}*"
        return s + (f" [[PDF]]({p['pdf']})" if p["pdf"] else "")

    paper_list = "\n".join(pline(p) for p in papers) if papers else "_Tidak ada paper hari ini._"

    materi_section = (
        f"## 📚 Materi: {topic['title']}\n\n"
        f"> Kategori: **{topic['category']}** | Tahun: **{topic['year']}**  \n"
        f"> File: [{topic['folder']}/README.md](../{topic['folder']}/README.md)\n\n"
        f"{materi}\n"
    ) if topic else "## 📚 Materi\n\n_Semua topik kurikulum sudah selesai!_\n"

    digest = (
        f"# Update Harian — {date_str}\n\n"
        f"> Diperbarui otomatis | Materi AI: {m_prov} | Berita AI: {n_prov}\n\n"
        f"---\n\n{materi_section}\n---\n\n"
        f"## 🔬 Paper Terbaru\n\n{paper_list}\n\n"
        f"### Rangkuman\n\n{news}\n\n"
        f"---\n_Update otomatis setiap hari pukul 07.00 WIB_\n"
    )
    daily_file = DAILY_DIR / f"{date_str}.md"
    daily_file.write_text(digest, encoding="utf-8")
    files.append(daily_file)

    # ── LATEST.md ───────────────────────────────────────────────────────────
    latest = (
        f"# Update Terbaru — {date_str}\n\n"
        + (f"**Materi:** [{topic['title']}](../{topic['folder']}/README.md)  \n"
           f"**Kategori:** {topic['category']}\n\n" if topic else "")
        + f"**Paper:** {len(papers)} paper\n\n---\n\n"
        f"[📖 Baca update lengkap hari ini](./{date_str}.md)\n\n"
        f"---\n\n### Cuplikan Materi\n\n" + materi[:500] + "\n\n...\n\n"
        f"### Cuplikan Berita\n\n" + news[:400] + "\n\n...\n\n"
        f"[→ Selengkapnya](./{date_str}.md)\n"
    )
    latest_file = DAILY_DIR / "LATEST.md"
    latest_file.write_text(latest, encoding="utf-8")
    files.append(latest_file)

    # ── News/LATEST.md ──────────────────────────────────────────────────────
    news_arc = NEWS_DIR / "Archive" / f"{date_str}.md"
    news_arc.write_text(
        f"# Berita Bioinformatika — {date_str}\n\n"
        f"> AI: {n_prov}\n\n---\n\n"
        f"## Paper\n\n{paper_list}\n\n---\n\n{news}\n",
        encoding="utf-8",
    )
    news_latest = NEWS_DIR / "LATEST.md"
    news_latest.write_text(
        f"# Berita Terbaru — {date_str}\n\n"
        f"{paper_list}\n\n---\n\n"
        + news[:1000] + f"\n\n[Lengkap →](./Archive/{date_str}.md)\n",
        encoding="utf-8",
    )
    files.extend([news_arc, news_latest])
    return files


# ══════════════════════════════════════════════════════════════════════════════
# GIT
# ══════════════════════════════════════════════════════════════════════════════

def git_push(date_str: str, files: list[Path], topic: dict | None) -> None:
    def run(cmd):
        subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)

    run(["git", "config", "user.name",  "github-actions[bot]"])
    run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])

    for f in files:
        if f.exists():
            run(["git", "add", str(f.relative_to(ROOT))])
    run(["git", "add", "README.md", "scripts/curriculum.json"])

    changed = subprocess.run(
        ["git", "diff", "--cached", "--quiet"], cwd=ROOT, capture_output=True
    ).returncode != 0

    if not changed:
        print("Tidak ada perubahan.")
        return

    label = topic["title"] if topic else "Update harian"
    run(["git", "commit", "-m", f"[Daily] {date_str}: {label}"])
    run(["git", "push"])
    print("Push berhasil ✓")


# ══════════════════════════════════════════════════════════════════════════════
# MAIN
# ══════════════════════════════════════════════════════════════════════════════

def main():
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"\n{'='*50}\nDAILY UPDATE: {date_str}\n{'='*50}")

    # 1. Materi kurikulum
    print("\n[1/3] Materi kurikulum...")
    data     = load_curriculum()
    topic    = next_topic(data)
    materi   = ""
    m_prov   = "-"

    if topic:
        print(f"  Topik: {topic['title']}")
        try:
            materi, m_prov = ai_generate(
                f"Buat materi belajar lengkap dalam Bahasa Indonesia:\n\n"
                f"**{topic['title']}**\nKategori: {topic['category']} | Tahun: {topic['year']}\n\n"
                f"Wajib ada:\n1. Definisi & konsep utama\n2. Sub-topik dengan penjelasan mendalam\n"
                f"3. Tabel atau diagram ASCII\n4. Contoh konkret\n5. Hubungan dengan bioinformatika\n"
                f"6. 5 pertanyaan latihan\n\nFormat: Markdown murni.",
                SYSTEM_MATERI,
            )
            mark_done(data, topic["id"])
            save_curriculum(data)
            update_progress(data)
        except Exception as e:
            print(f"  Materi gagal: {e}")
            topic = None
    else:
        print("  Semua topik selesai!")

    # 2. Paper terbaru
    print("\n[2/3] Fetch paper...")
    papers = []
    try:
        papers = collect_papers()
        print(f"  {len(papers)} paper ditemukan.")
    except Exception as e:
        print(f"  Fetch gagal: {e}")

    news   = ""
    n_prov = "-"
    try:
        if papers:
            pt = "".join(
                f"\n### {i}. {p['title']}\nVenue: {p['journal']} ({p['year']})\n{p['abstract']}\n"
                for i, p in enumerate(papers, 1)
            )
            prompt = (
                f"Rangkum {len(papers)} paper bioinformatika ini dalam Bahasa Indonesia:\n{pt}\n\n"
                f"1. Jelaskan tiap paper 3-4 kalimat untuk pemula\n"
                f"2. Teknologi/metode utama\n3. Mengapa penting\n"
                f"4. **Istilah Kunci** (3-5 istilah)\n5. **Koneksi ke Kurikulum**"
            )
        else:
            prompt = (
                f"Buat update bioinformatika harian ({date_str}) dalam Bahasa Indonesia. "
                f"Pilih 1 topik bioinformatika trending, jelaskan untuk pemula (3-4 paragraf), "
                f"sertakan **Istilah Kunci** dan **Sumber Belajar**."
            )
        news, n_prov = ai_generate(prompt, SYSTEM_NEWS)
    except Exception as e:
        print(f"  Rangkuman gagal: {e}")
        news = "_Rangkuman tidak tersedia hari ini._"

    # 3. Tulis & push
    print("\n[3/3] Tulis file & push...")
    files = write_all(date_str, topic, materi, m_prov, papers, news, n_prov)
    git_push(date_str, files, topic)

    print(f"\n✓ Selesai! Materi: {topic['title'] if topic else '-'} | Paper: {len(papers)}")


if __name__ == "__main__":
    main()
