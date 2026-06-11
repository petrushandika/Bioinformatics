# Genetika

## Apa itu Genetika?

**Genetika** adalah cabang biologi yang mempelajari gen, pewarisan sifat, dan variasi pada organisme. Kata "genetika" berasal dari bahasa Yunani *genesis* (asal-usul).

---

## Hukum Mendel

### Gregor Mendel (1822–1884)

Bapa genetika modern. Melakukan percobaan pada ~29.000 tanaman kacang polong (*Pisum sativum*) selama 8 tahun.

### Hukum I Mendel — Segregasi

> *"Dua alel untuk sifat tertentu dipisahkan saat pembentukan gamet, sehingga setiap gamet hanya membawa satu alel."*

**Contoh:**

```
Orang tua:  Tt  ×  Tt
            ↓
Gamet:   T,t    ×   T,t

Bagan Punnett:
      T      t
T  | TT  |  Tt  |
t  | Tt  |  tt  |

Rasio genotip:  1 TT : 2 Tt : 1 tt
Rasio fenotip:  3 Tinggi : 1 Pendek
```

### Hukum II Mendel — Pemisahan Bebas

> *"Gen untuk sifat yang berbeda diwariskan secara bebas satu sama lain."*

```
Orang tua:  BBTT  ×  bbtt
F1:         BbTt  (semua)
F2 rasio:   9:3:3:1
```

---

## Terminologi Genetika

| Istilah | Definisi |
|---------|----------|
| Gen | Segmen DNA yang mengkode protein/RNA fungsional |
| Alel | Varian dari gen yang sama |
| Genotip | Komposisi genetik (TT, Tt, tt) |
| Fenotip | Ekspresi fisik/tampak dari gen |
| Dominan | Alel yang diekspresikan (T) |
| Resesif | Alel yang tersembunyi saat berpasangan (t) |
| Homozigot | Dua alel identik (TT atau tt) |
| Heterozigot | Dua alel berbeda (Tt) |
| Lokus | Posisi gen pada kromosom |

---

## Kromosom

### Struktur Kromosom

```
Kromosom terdiri dari:
- DNA (untai panjang)
- Histon (protein pengemas)
- Scaffold protein

Tingkatan kemasan:
DNA → Nukleosom → Solenoid → Loop → Kromosom
```

### Jumlah Kromosom

| Organisme | Jumlah Kromosom (2n) |
|-----------|----------------------|
| Manusia | 46 (23 pasang) |
| Tikus | 40 |
| Nyamuk | 6 |
| Semangka | 22 |
| Bawang | 16 |
| Lalat buah (*Drosophila*) | 8 |

### Kromosom Seks

- **Perempuan:** XX
- **Laki-laki:** XY

---

## Pola Pewarisan

### 1. Dominan Autosomal

```
Ciri: Sifat muncul di setiap generasi
Contoh: Penyakit Huntington, Polidaktili
Pola:  Aa × aa → 1/2 anak terpengaruh
```

### 2. Resesif Autosomal

```
Ciri: Gen dibawa oleh carrier tanpa gejala
Contoh: Fibrosis Kistik, Anemia Sel Sabit
Pola:  Aa × Aa → 1/4 anak terpengaruh
```

### 3. X-Linked

```
Ciri: Gen pada kromosom X
Contoh: Buta Warna, Hemofilia
Laki-laki (XY) lebih sering terdampak
karena hanya memiliki 1 kromosom X
```

### 4. Kodominans

```
Ciri: Kedua alel diekspresikan bersamaan
Contoh: Golongan Darah ABO
  Alel: Iᴬ (A), Iᴮ (B), i (O)
  IᴬIᴮ = Golongan Darah AB
```

---

## Golongan Darah ABO

| Genotip | Golongan |
|---------|----------|
| IᴬIᴬ atau Iᴬi | A |
| IᴮIᴮ atau Iᴮi | B |
| IᴬIᴮ | AB |
| ii | O |

---

## Mutasi dan Penyakit Genetik

### Contoh Penyakit Genetik

| Penyakit | Tipe | Penyebab |
|----------|------|----------|
| Down Syndrome | Kromosomal | Trisomi 21 (3 kromosom ke-21) |
| Turner Syndrome | Kromosomal | XO (hanya 1 kromosom X) |
| Klinefelter | Kromosomal | XXY |
| Anemia Sel Sabit | Titik mutasi | Glu→Val pada HbS |
| Fibrosis Kistik | Resesif | Mutasi gen CFTR |
| Hemofilia A | X-linked | Mutasi gen F8 |

---

## Epigenetik

Perubahan ekspresi gen **tanpa perubahan sekuens DNA**.

```
Mekanisme Epigenetik:
┌─────────────────────────────┐
│ Metilasi DNA               │  ─── CpG island → gen dimatikan
│ Modifikasi Histon          │  ─── Asetilasi → gen dinyalakan
│ RNA non-coding             │  ─── miRNA → post-translational silencing
│ Remodeling Kromatin        │  ─── Buka/tutup akses DNA
└─────────────────────────────┘
```

**Fakta menarik:** Kembar identik memiliki DNA sama, tetapi ekspresi gen dapat berbeda karena epigenetik!

---

## Genetika Populasi

### Hukum Hardy-Weinberg

Frekuensi alel dalam populasi tetap konstan **jika**:
- Populasi besar
- Perkawinan acak
- Tidak ada mutasi
- Tidak ada migrasi
- Tidak ada seleksi alam

```
Formula: p² + 2pq + q² = 1
         p + q = 1

p = frekuensi alel dominan (A)
q = frekuensi alel resesif (a)
p² = frekuensi AA
2pq = frekuensi Aa
q² = frekuensi aa
```

---

## Relevansi dengan Bioinformatika

```
Genetika → Bioinformatika

Sekuens gen       → Gene annotation, database GenBank
SNP (variasi)     → GWAS (Genome-Wide Association Study)
Pewarisan sifat   → Pemodelan pedigree komputasional
Penyakit genetik  → Clinical variant interpretation
Genetika populasi → Population genomics, phylogenetics
Epigenetik        → ChIP-seq, WGBS analysis
```

---

## Pertanyaan Latihan

1. Apa perbedaan genotip dan fenotip?
2. Jika Aa × Aa, berapa probabilitas anak aa?
3. Mengapa hemofilia lebih sering pada laki-laki?
4. Apa yang dimaksud dengan Hukum Hardy-Weinberg?
5. Bagaimana epigenetik berbeda dari mutasi DNA?

---

_[← Kembali: Biologi Molekuler](../03-Molecular-Biology/README.md) | [Lanjut: Biokimia →](../05-Biochemistry/README.md)_
