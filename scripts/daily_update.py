#!/usr/bin/env python3
"""
daily_update.py
Generates one new learning material per day using Claude API,
commits it to the repository, and updates LATEST.md + README progress.
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
import subprocess
import anthropic

# ── Paths ────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
CURRICULUM_FILE = Path(__file__).parent / "curriculum.json"
DAILY_DIR = ROOT / "Daily"
LATEST_FILE = DAILY_DIR / "LATEST.md"


# ── Helpers ──────────────────────────────────────────────────────────────────

def load_curriculum() -> dict:
    with open(CURRICULUM_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_curriculum(data: dict) -> None:
    with open(CURRICULUM_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def get_next_topic(data: dict) -> dict | None:
    """Return the first topic with status='pending'."""
    for topic in data["curriculum"]:
        if topic["status"] == "pending":
            return topic
    return None


def mark_done(data: dict, topic_id: str) -> None:
    for topic in data["curriculum"]:
        if topic["id"] == topic_id:
            topic["status"] = "done"
            break


def run(cmd: list[str], cwd: Path = ROOT) -> None:
    result = subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)


# ── Claude content generation ─────────────────────────────────────────────────

def generate_content(topic: dict) -> str:
    """Call Claude API to generate markdown content for the topic."""
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])

    system = (
        "Kamu adalah pengajar bioinformatika yang membuat materi belajar dalam Bahasa Indonesia. "
        "Tulis konten markdown yang komprehensif, terstruktur, dan mudah dipahami oleh pemula. "
        "Gunakan contoh nyata, diagram ASCII jika relevan, tabel, dan pertanyaan latihan. "
        "Akhiri selalu dengan bagian '## Pertanyaan Latihan' (5 soal) dan '## Relevansi dengan Bioinformatika'."
    )

    prompt = (
        f"Buat materi pembelajaran lengkap dalam Bahasa Indonesia untuk topik:\n\n"
        f"**{topic['title']}**\n"
        f"Kategori: {topic['category']}\n"
        f"Tahun kurikulum: {topic['year']}\n\n"
        f"Sertakan:\n"
        f"1. Definisi dan konsep utama\n"
        f"2. Sub-topik penting dengan penjelasan mendalam\n"
        f"3. Tabel atau diagram ASCII yang relevan\n"
        f"4. Contoh-contoh konkret\n"
        f"5. Hubungan dengan topik bioinformatika\n"
        f"6. Pertanyaan latihan (5 soal)\n\n"
        f"Format output: Markdown murni, siap disimpan sebagai README.md."
    )

    message = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
        system=system,
    )

    return message.content[0].text


# ── Daily log ─────────────────────────────────────────────────────────────────

def write_daily_log(topic: dict, content: str, date_str: str) -> Path:
    """Write dated daily file and update LATEST.md."""
    DAILY_DIR.mkdir(exist_ok=True)

    dated_file = DAILY_DIR / f"{date_str}.md"
    header = (
        f"# Update Harian — {date_str}\n\n"
        f"> **Topik hari ini:** {topic['title']}  \n"
        f"> **Kategori:** {topic['category']}  \n"
        f"> **Tahun Kurikulum:** {topic['year']}  \n"
        f"> **File:** [{topic['folder']}/README.md](../{topic['folder']}/README.md)\n\n"
        f"---\n\n"
    )
    dated_file.write_text(header + content, encoding="utf-8")

    # Update LATEST.md to point to today
    latest_content = (
        f"# Materi Terbaru\n\n"
        f"**Diperbarui:** {date_str}\n\n"
        f"**Topik:** {topic['title']}  \n"
        f"**Kategori:** {topic['category']}\n\n"
        f"---\n\n"
        f"📄 Baca log lengkap hari ini: [{date_str}.md](./{date_str}.md)\n\n"
        f"📚 Baca materi: [{topic['folder']}/README.md](../{topic['folder']}/README.md)\n\n"
        f"---\n\n"
        f"## Ringkasan\n\n"
        + content[:800]
        + "\n\n...\n\n"
        + f"_[Baca selengkapnya →](./{date_str}.md)_\n"
    )
    LATEST_FILE.write_text(latest_content, encoding="utf-8")

    return dated_file


# ── README progress updater ───────────────────────────────────────────────────

def update_readme_progress(data: dict) -> None:
    """Update progress bar in README.md based on curriculum status."""
    readme = ROOT / "README.md"
    text = readme.read_text(encoding="utf-8")

    counts: dict[str, dict] = {}
    for topic in data["curriculum"]:
        cat = topic["category"]
        if cat not in counts:
            counts[cat] = {"done": 0, "total": 0}
        counts[cat]["total"] += 1
        if topic["status"] == "done":
            counts[cat]["done"] += 1

    def bar(done: int, total: int, width: int = 10) -> str:
        filled = round((done / total) * width) if total else 0
        pct = round((done / total) * 100) if total else 0
        return f"{'█' * filled}{'░' * (width - filled)}  {pct:3d}%"

    bio = counts.get("Biology", {"done": 0, "total": 1})
    py = counts.get("Python", {"done": 0, "total": 1})
    math = counts.get("Mathematics", {"done": 0, "total": 1})
    bioinf = counts.get("Bioinformatics", {"done": 0, "total": 1})
    ml = counts.get("MachineLearning", {"done": 0, "total": 1})

    new_progress = (
        "```\n"
        f"Biologi         {bar(bio['done'], bio['total'])}\n"
        f"Python          {bar(py['done'], py['total'])}\n"
        f"Matematika      {bar(math['done'], math['total'])}\n"
        f"Bioinformatika  {bar(bioinf['done'], bioinf['total'])}\n"
        f"Machine Learning{bar(ml['done'], ml['total'])}\n"
        "```"
    )

    import re
    text = re.sub(r"```\nBiologi.*?```", new_progress, text, flags=re.DOTALL)
    readme.write_text(text, encoding="utf-8")


# ── Git operations ─────────────────────────────────────────────────────────────

def git_commit_and_push(topic: dict, date_str: str, files: list[Path]) -> None:
    run(["git", "config", "user.name", "github-actions[bot]"])
    run(["git", "config", "user.email", "github-actions[bot]@users.noreply.github.com"])

    for f in files:
        run(["git", "add", str(f.relative_to(ROOT))], cwd=ROOT)

    run(["git", "add", "scripts/curriculum.json", "README.md"])

    msg = f"[Daily] {date_str}: {topic['title']} ({topic['category']})"
    run(["git", "commit", "-m", msg])
    run(["git", "push"])


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    print(f"=== Daily Update: {date_str} ===")

    # Load curriculum
    data = load_curriculum()
    topic = get_next_topic(data)

    if topic is None:
        print("Semua materi sudah selesai! Tidak ada update hari ini.")
        sys.exit(0)

    print(f"Topik: {topic['title']} ({topic['id']})")

    # Generate content
    print("Generating content via Claude API...")
    content = generate_content(topic)

    # Create topic folder & file
    topic_dir = ROOT / topic["folder"]
    topic_dir.mkdir(parents=True, exist_ok=True)
    topic_readme = topic_dir / "README.md"
    topic_readme.write_text(content, encoding="utf-8")
    print(f"Ditulis: {topic_readme}")

    # Write daily log
    dated_log = write_daily_log(topic, content, date_str)
    print(f"Log harian: {dated_log}")

    # Mark done & update progress
    mark_done(data, topic["id"])
    save_curriculum(data)
    update_readme_progress(data)

    # Commit & push
    print("Committing to GitHub...")
    git_commit_and_push(topic, date_str, [topic_readme, dated_log, LATEST_FILE])

    print(f"Selesai! Materi '{topic['title']}' berhasil dipush ke GitHub.")


if __name__ == "__main__":
    main()
