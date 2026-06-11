#!/usr/bin/env python3
"""
daily_update.py
Generates one new learning material per day using a free AI API,
commits it to the repository, and updates LATEST.md + README progress.
"""

import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
import subprocess

from ai_client import generate

ROOT = Path(__file__).parent.parent
CURRICULUM_FILE = Path(__file__).parent / "curriculum.json"
DAILY_DIR = ROOT / "Daily"
LATEST_FILE = DAILY_DIR / "LATEST.md"

SYSTEM = (
    "Kamu adalah pengajar bioinformatika yang membuat materi belajar dalam Bahasa Indonesia. "
    "Tulis konten markdown yang komprehensif, terstruktur, dan mudah dipahami oleh pemula. "
    "Gunakan contoh nyata, diagram ASCII jika relevan, tabel, dan pertanyaan latihan. "
    "Akhiri selalu dengan bagian '## Pertanyaan Latihan' (5 soal) dan '## Relevansi dengan Bioinformatika'."
)


def load_curriculum() -> dict:
    with open(CURRICULUM_FILE, encoding="utf-8") as f:
        return json.load(f)


def save_curriculum(data: dict) -> None:
    with open(CURRICULUM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_next_topic(data: dict) -> dict | None:
    for topic in data["curriculum"]:
        if topic["status"] == "pending":
            return topic
    return None


def mark_done(data: dict, topic_id: str) -> None:
    for t in data["curriculum"]:
        if t["id"] == topic_id:
            t["status"] = "done"
            break


def generate_content(topic: dict) -> tuple[str, str]:
    prompt = (
        f"Buat materi pembelajaran lengkap dalam Bahasa Indonesia untuk topik:\n\n"
        f"**{topic['title']}**\n"
        f"Kategori: {topic['category']} | Tahun kurikulum: {topic['year']}\n\n"
        f"Sertakan:\n"
        f"1. Definisi dan konsep utama\n"
        f"2. Sub-topik penting dengan penjelasan mendalam\n"
        f"3. Tabel atau diagram ASCII yang relevan\n"
        f"4. Contoh-contoh konkret\n"
        f"5. Hubungan dengan topik bioinformatika\n"
        f"6. Pertanyaan latihan (5 soal)\n\n"
        f"Format output: Markdown murni, siap disimpan sebagai README.md."
    )
    return generate(prompt, SYSTEM)


def write_daily_log(topic: dict, content: str, provider: str, date_str: str) -> Path:
    DAILY_DIR.mkdir(exist_ok=True)
    dated_file = DAILY_DIR / f"{date_str}.md"
    header = (
        f"# Update Harian — {date_str}\n\n"
        f"> **Topik:** {topic['title']}  \n"
        f"> **Kategori:** {topic['category']}  \n"
        f"> **Tahun Kurikulum:** {topic['year']}  \n"
        f"> **AI Provider:** {provider}  \n"
        f"> **File:** [{topic['folder']}/README.md](../{topic['folder']}/README.md)\n\n"
        f"---\n\n"
    )
    dated_file.write_text(header + content, encoding="utf-8")

    LATEST_FILE.write_text(
        f"# Materi Terbaru\n\n"
        f"**Diperbarui:** {date_str}  \n"
        f"**Topik:** {topic['title']}  \n"
        f"**Kategori:** {topic['category']}  \n"
        f"**AI Provider:** {provider}\n\n"
        f"---\n\n"
        f"📄 Log lengkap: [{date_str}.md](./{date_str}.md)\n\n"
        f"📚 Materi: [{topic['folder']}/README.md](../{topic['folder']}/README.md)\n\n"
        f"---\n\n"
        + content[:800]
        + "\n\n...\n\n_[Baca selengkapnya →](./{}.md)_\n".format(date_str),
        encoding="utf-8",
    )
    return dated_file


def update_readme_progress(data: dict) -> None:
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")

    counts: dict[str, dict] = {}
    for t in data["curriculum"]:
        cat = t["category"]
        counts.setdefault(cat, {"done": 0, "total": 0})
        counts[cat]["total"] += 1
        if t["status"] == "done":
            counts[cat]["done"] += 1

    def bar(done: int, total: int, w: int = 10) -> str:
        f = round((done / total) * w) if total else 0
        pct = round((done / total) * 100) if total else 0
        return f"{'█' * f}{'░' * (w - f)}  {pct:3d}%"

    def c(cat):
        return counts.get(cat, {"done": 0, "total": 1})

    new_progress = (
        "```\n"
        f"Biologi         {bar(c('Biology')['done'], c('Biology')['total'])}\n"
        f"Python          {bar(c('Python')['done'], c('Python')['total'])}\n"
        f"Matematika      {bar(c('Mathematics')['done'], c('Mathematics')['total'])}\n"
        f"Bioinformatika  {bar(c('Bioinformatics')['done'], c('Bioinformatics')['total'])}\n"
        f"Machine Learning{bar(c('MachineLearning')['done'], c('MachineLearning')['total'])}\n"
        "```"
    )
    text = re.sub(r"```\nBiologi.*?```", new_progress, text, flags=re.DOTALL)
    readme.write_text(text, encoding="utf-8")


def git_commit_and_push(topic: dict, date_str: str, files: list[Path]) -> None:
    def run(cmd):
        subprocess.run(cmd, cwd=ROOT, check=True, capture_output=True, text=True)

    run(["git", "config", "user.name", "github-actions[bot]"])
    run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])
    for f in files:
        run(["git", "add", str(f.relative_to(ROOT))])
    run(["git", "add", "scripts/curriculum.json", "README.md"])
    run(["git", "commit", "-m", f"[Daily] {date_str}: {topic['title']} ({topic['category']})"])
    run(["git", "push"])


def main() -> None:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"=== Daily Update: {date_str} ===")

    data = load_curriculum()
    topic = get_next_topic(data)
    if topic is None:
        print("Semua materi selesai!")
        sys.exit(0)

    print(f"Topik: {topic['title']}")
    content, provider = generate_content(topic)

    topic_dir = ROOT / topic["folder"]
    topic_dir.mkdir(parents=True, exist_ok=True)
    topic_readme = topic_dir / "README.md"
    topic_readme.write_text(content, encoding="utf-8")

    dated_log = write_daily_log(topic, content, provider, date_str)
    mark_done(data, topic["id"])
    save_curriculum(data)
    update_readme_progress(data)

    git_commit_and_push(topic, date_str, [topic_readme, dated_log, LATEST_FILE])
    print(f"Selesai! '{topic['title']}' berhasil dipush ({provider}).")


if __name__ == "__main__":
    main()
