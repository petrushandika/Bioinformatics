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

<!-- CURRICULUM:START -->
### Tahun 1 — Fondasi

| Status | Kategori | Topik | Folder |
|--------|----------|-------|--------|
| ✅ | 🧬 Biologi | Sejarah Biologi & Bioinformatika | [Biology/01-History](./Biology/01-History/) |
| ✅ | 🧬 Biologi | Struktur Sel | [Biology/02-Cell-Structure](./Biology/02-Cell-Structure/) |
| ✅ | 🧬 Biologi | Biologi Molekuler & Dogma Sentral | [Biology/03-Molecular-Biology](./Biology/03-Molecular-Biology/) |
| ✅ | 🧬 Biologi | Genetika & Hukum Mendel | [Biology/04-Genetics](./Biology/04-Genetics/) |
| ✅ | 🧬 Biologi | Biokimia Dasar | [Biology/05-Biochemistry](./Biology/05-Biochemistry/) |
| 🔜 | 🧬 Biologi | Struktur & Fungsi Protein | `Biology/06-Protein/` |
| 🔜 | 🧬 Biologi | Enzim & Kinetika Enzim | `Biology/07-Enzyme/` |
| 🔜 | 🧬 Biologi | Metabolisme Seluler (Glikolisis & Respirasi) | `Biology/08-Metabolism/` |
| 🔜 | 🧬 Biologi | Evolusi & Seleksi Alam | `Biology/09-Evolution/` |
| 🔜 | 🧬 Biologi | Taksonomi & Klasifikasi Makhluk Hidup | `Biology/10-Taxonomy/` |
| 🔜 | 💻 Python | Fungsi & Modul dalam Python | `Python/01-Basics/08-Function/` |
| 🔜 | 💻 Python | File I/O dalam Python | `Python/01-Basics/09-File-IO/` |
| 🔜 | 💻 Python | List & Tuple dalam Python | `Python/01-Basics/10-List-Tuple/` |
| 🔜 | 💻 Python | Dictionary & Set dalam Python | `Python/01-Basics/11-Dict-Set/` |
| 🔜 | 💻 Python | Loop (For & While) dalam Python | `Python/01-Basics/12-Loop/` |
| 🔜 | 💻 Python | Pemrograman Berorientasi Objek (OOP) | `Python/01-Basics/13-OOP/` |
| 🔜 | 💻 Python | Error Handling & Exception | `Python/01-Basics/14-Exception/` |
| 🔜 | 💻 Python | List Comprehension & Lambda | `Python/01-Basics/15-Comprehension/` |
| 🔜 | 📊 Matematika & Statistik | Aljabar Dasar untuk Bioinformatika | `Mathematics/01-Algebra/` |
| 🔜 | 📊 Matematika & Statistik | Statistika Deskriptif | `Mathematics/02-Statistics/` |
| 🔜 | 📊 Matematika & Statistik | Probabilitas & Distribusi | `Mathematics/03-Probability/` |

### Tahun 2 — Konsep Inti

| Status | Kategori | Topik | Folder |
|--------|----------|-------|--------|
| 🔜 | 📊 Matematika & Statistik | Aljabar Linear & Matriks | `Mathematics/04-Linear-Algebra/` |
| 🔜 | 🧬 Biologi | Sekuensing DNA & NGS | `Biology/11-DNA-Sequencing/` |
| 🔜 | 🔬 Bioinformatika | BLAST & Sequence Alignment | `Bioinformatics/01-BLAST/` |
| 🔜 | 🔬 Bioinformatika | Pengenalan BioPython | `Bioinformatics/02-BioPython/` |
| 🔜 | 🔬 Bioinformatika | Analisis Sekuens dengan Python | `Bioinformatics/03-Sequence-Analysis/` |
| 🔜 | 🔬 Bioinformatika | Pairwise Sequence Alignment | `Bioinformatics/04-Pairwise-Alignment/` |
| 🔜 | 🔬 Bioinformatika | Multiple Sequence Alignment | `Bioinformatics/05-MSA/` |
| 🔜 | 🖥️ Komputasi | Linux & Shell Scripting untuk Bioinformatika | `Computing/01-Linux-Shell/` |
| 🔜 | 🖥️ Komputasi | Database & SQL untuk Data Biologis | `Computing/02-Database-SQL/` |
| 🔜 | 🔬 Bioinformatika | Format File Biologis: FASTA, FASTQ, GenBank, SAM/BAM, VCF | `Bioinformatics/07-File-Formats/` |
| 🔜 | 🔬 Bioinformatika | Database Biologis: NCBI, UniProt, Ensembl, PDB | `Bioinformatics/08-Biological-Databases/` |
| 🔜 | 📊 Matematika & Statistik | Uji Hipotesis & p-value | `Mathematics/05-Hypothesis-Testing/` |
| 🔜 | 📊 Matematika & Statistik | Statistik dengan R | `Mathematics/06-Statistics-with-R/` |

### Tahun 3 — Spesialisasi

| Status | Kategori | Topik | Folder |
|--------|----------|-------|--------|
| 🔜 | 🔬 Bioinformatika | Analisis Filogenetik | `Bioinformatics/06-Phylogenetics/` |
| 🔜 | 🤖 Machine Learning | Pengenalan Machine Learning untuk Bioinformatika | `MachineLearning/01-Intro/` |
| 🔜 | 🤖 Machine Learning | Scikit-learn untuk Analisis Biologis | `MachineLearning/02-Sklearn/` |
| 🔜 | 🔬 Bioinformatika | Hidden Markov Model untuk Analisis Sekuens | `Bioinformatics/09-Hidden-Markov-Model/` |
| 🔜 | 🔬 Bioinformatika | Prediksi Struktur Protein & AlphaFold | `Bioinformatics/10-Protein-Structure-Prediction/` |
| 🔜 | 📊 Matematika & Statistik | Biostatistik: Multiple Testing & False Discovery Rate | `Mathematics/07-Multiple-Testing/` |
| 🔜 | 🔬 Bioinformatika | RNA-seq & Analisis Ekspresi Gen Diferensial | `Bioinformatics/11-RNA-Seq-Differential-Expression/` |
| 🔜 | 🔬 Bioinformatika | Genome Assembly | `Bioinformatics/12-Genome-Assembly/` |
| 🔜 | 🔬 Bioinformatika | Variant Calling & Anotasi Varian | `Bioinformatics/13-Variant-Calling/` |
| 🔜 | 🔬 Bioinformatika | Gene Ontology & Pathway Enrichment | `Bioinformatics/14-Gene-Ontology-Enrichment/` |
| 🔜 | 🤖 Machine Learning | Clustering & PCA untuk Data Ekspresi Gen | `MachineLearning/04-Clustering-PCA/` |

### Tahun 4 — Aplikasi Lanjutan

| Status | Kategori | Topik | Folder |
|--------|----------|-------|--------|
| 🔜 | 🤖 Machine Learning | Deep Learning untuk Genomik | `MachineLearning/03-Deep-Learning/` |
| 🔜 | 🔬 Bioinformatika | Analisis Single-cell RNA-seq | `Bioinformatics/15-Single-Cell/` |
| 🔜 | 🔬 Bioinformatika | Metagenomik & Analisis Mikrobioma | `Bioinformatics/16-Metagenomics/` |
| 🔜 | 🖥️ Komputasi | Workflow Reproducible: Snakemake & Nextflow | `Computing/03-Reproducible-Workflows/` |
| 🔜 | 🔬 Bioinformatika | Bioinformatika Struktural & Molecular Docking | `Bioinformatics/17-Structural-Bioinformatics/` |
| 🔜 | 🤖 Machine Learning | Protein Language Models | `MachineLearning/05-Protein-Language-Models/` |
| 🔜 | 🎓 Capstone | Proyek Capstone: Pipeline Analisis Genomik End-to-end | `Capstone/01-Final-Project/` |

<!-- CURRICULUM:END -->

---

## Progress Belajar

<!-- PROGRESS:START -->
```
Biologi                 █████░░░░░  5/11  45%
Python                  ░░░░░░░░░░  0/8    0%
Matematika & Statistik  ░░░░░░░░░░  0/7    0%
Bioinformatika          ░░░░░░░░░░  0/17   0%
Machine Learning        ░░░░░░░░░░  0/5    0%
Komputasi               ░░░░░░░░░░  0/3    0%
Capstone                ░░░░░░░░░░  0/1    0%
Total                   █░░░░░░░░░  5/52  10%
```
<!-- PROGRESS:END -->

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
