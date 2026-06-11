# Bioinformatics Learning Journey 🧬

Repositori ini mendokumentasikan perjalanan belajar bioinformatika secara terstruktur — mulai dari konsep dasar biologi, pemrograman Python, hingga analisis data genomik tingkat lanjut. Materi diperbarui otomatis setiap hari melalui GitHub Actions.

---

## Daftar Isi

- [Tentang Proyek](#tentang-proyek)
- [Motivasi](#motivasi)
- [Struktur Folder](#struktur-folder)
- [Kurikulum](#kurikulum)
- [Progress Belajar](#progress-belajar)
- [Pembaruan Harian](#pembaruan-harian)
- [Tools & Teknologi](#tools--teknologi)
- [Referensi](#referensi)

---

## Tentang Proyek

Repositori ini adalah catatan perjalanan belajar bioinformatika yang mengikuti kurikulum terstruktur dari [OSSU Bioinformatics](https://github.com/ossu/bioinformatics). Setiap folder berisi file markdown berisi teori, konsep, dan kode yang relevan.

> Materi baru ditambahkan otomatis setiap hari. Cek folder [`Daily/`](./Daily/) untuk log harian terbaru.

---

## Motivasi

Bioinformatika adalah persimpangan antara biologi, ilmu komputer, dan analisis data. Perjalanan ini dimotivasi oleh:

- Memahami aspek komputasional dalam penelitian biologi
- Mengembangkan kemampuan memproses dan menganalisis data biologis
- Berkontribusi pada bidang biologi komputasional yang berkembang pesat
- Menjembatani ilmu biologi dengan pemrograman komputer
- Menguasai tools dan praktik standar industri bioinformatika

---

## Struktur Folder

```
Bioinformatics/
├── README.md                    ← Halaman utama (file ini)
├── Daily/                       ← Log & materi harian (auto-update)
│   ├── LATEST.md               ← Materi terbaru hari ini
│   └── YYYY-MM-DD.md           ← Arsip per tanggal
├── Biology/                     ← Materi biologi
│   ├── 01-History/             ← Sejarah biologi & bioinformatika
│   ├── 02-Cell-Structure/      ← Struktur sel
│   ├── 03-Molecular-Biology/   ← Biologi molekuler
│   ├── 04-Genetics/            ← Genetika
│   └── 05-Biochemistry/        ← Biokimia dasar
├── Python/                      ← Pemrograman Python
│   └── 01-Basics/              ← Dasar-dasar Python
│       ├── 01-Intro/
│       ├── 02-Comment/
│       ├── 03-Variable/
│       ├── 04-Data-Type/
│       ├── 05-String/
│       ├── 06-Operator/
│       └── 07-Control-Program/
└── .github/
    └── workflows/
        └── daily-update.yml    ← Otomatisasi GitHub Actions
```

---

## Kurikulum

### Tahun 1 — Fondasi

#### 🧬 Biologi Dasar

| Status | Topik | Folder |
|--------|-------|--------|
| ✅ | Sejarah Biologi & Bioinformatika | [Biology/01-History](./Biology/01-History/) |
| ✅ | Struktur Sel | [Biology/02-Cell-Structure](./Biology/02-Cell-Structure/) |
| ✅ | Biologi Molekuler | [Biology/03-Molecular-Biology](./Biology/03-Molecular-Biology/) |
| ✅ | Genetika | [Biology/04-Genetics](./Biology/04-Genetics/) |
| ✅ | Biokimia Dasar | [Biology/05-Biochemistry](./Biology/05-Biochemistry/) |

#### 💻 Pemrograman Python

| Status | Topik | Folder |
|--------|-------|--------|
| ✅ | Intro & Hello World | [Python/01-Basics/01-Intro](./Python/01-Basics/01-Intro/) |
| ✅ | Komentar | [Python/01-Basics/02-Comment](./Python/01-Basics/02-Comment/) |
| ✅ | Variable | [Python/01-Basics/03-Variable](./Python/01-Basics/03-Variable/) |
| ✅ | Tipe Data | [Python/01-Basics/04-Data-Type](./Python/01-Basics/04-Data-Type/) |
| ✅ | String & Manipulasi | [Python/01-Basics/05-String](./Python/01-Basics/05-String/) |
| ✅ | Operator | [Python/01-Basics/06-Operator](./Python/01-Basics/06-Operator/) |
| ✅ | Kontrol Program | [Python/01-Basics/07-Control-Program](./Python/01-Basics/07-Control-Program/) |
| 🔜 | Fungsi & Modul | Python/01-Basics/08-Function/ |
| 🔜 | File I/O | Python/01-Basics/09-File-IO/ |
| 🔜 | List & Tuple | Python/01-Basics/10-List-Tuple/ |
| 🔜 | Dictionary & Set | Python/01-Basics/11-Dict-Set/ |

#### 📊 Matematika & Statistik

| Status | Topik |
|--------|-------|
| 🔜 | Aljabar & Fungsi |
| 🔜 | Kalkulus Dasar |
| 🔜 | Statistik dengan R |

---

### Tahun 2 — Konsep Inti

| Status | Topik |
|--------|-------|
| 🔜 | Biokimia Lanjutan (Protein, Enzim) |
| 🔜 | OOP dengan Java |
| 🔜 | Database & SQL |
| 🔜 | Linux & Shell Scripting |
| 🔜 | BioPython |
| 🔜 | BLAST & Sequence Analysis |

---

### Tahun 3 — Topik Spesialisasi

| Status | Topik |
|--------|-------|
| 🔜 | Multiple Sequence Alignment |
| 🔜 | Prediksi Struktur Protein |
| 🔜 | Machine Learning Dasar |
| 🔜 | Biostatistik |

---

### Tahun 4 — Aplikasi Lanjutan

| Status | Topik |
|--------|-------|
| 🔜 | Genomics & Transcriptomics |
| 🔜 | Next-Generation Sequencing |
| 🔜 | Deep Learning untuk Genomik |
| 🔜 | Proyek Capstone |

---

## Progress Belajar

```
Biologi         ████░░░░░░  20%
Python          ███░░░░░░░  30%
Matematika      ░░░░░░░░░░   0%
Bioinformatika  ░░░░░░░░░░   0%
Machine Learning░░░░░░░░░░   0%
```

---

## Pembaruan Harian

Setiap hari, GitHub Actions secara otomatis menambahkan konten baru ke folder [`Daily/`](./Daily/). Ini mencakup:

- Ringkasan topik baru
- Catatan belajar harian
- Kode contoh
- Pertanyaan latihan

**Untuk membaca update terbaru:** buka [`Daily/LATEST.md`](./Daily/LATEST.md)

---

## Tools & Teknologi

| Kategori | Tools |
|----------|-------|
| Bahasa Pemrograman | Python, R, Java |
| Bioinformatika | BioPython, Bioconductor, BLAST |
| Analisis Data | Pandas, NumPy, SciPy |
| Visualisasi | Matplotlib, ggplot2 |
| Database | GenBank, UniProt, NCBI |
| Workflow | GitHub Actions |

---

## Referensi

Kurikulum ini mengikuti [OSSU Bioinformatics Curriculum](https://github.com/ossu/bioinformatics) dan dilengkapi dengan:

1. **Kursus Online**
   - edX, Coursera, MIT OpenCourseWare

2. **Buku Teks**
   - *Bioinformatics and Functional Genomics* — Jonathan Pevsner
   - *Python for Biologists* — Martin Jones
   - *Statistical Methods in Bioinformatics* — William Ewens

3. **Sumber Online**
   - [NCBI](https://www.ncbi.nlm.nih.gov/)
   - [European Bioinformatics Institute](https://www.ebi.ac.uk/)
   - [Galaxy Project](https://galaxyproject.org/)

---

## Lisensi

Repositori ini dilisensikan di bawah MIT License.

---

_Repositori ini diperbarui otomatis setiap hari. Terakhir diperbarui: lihat [Daily/LATEST.md](./Daily/LATEST.md)_
