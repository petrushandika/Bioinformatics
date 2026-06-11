# Biologi Molekuler

## Apa itu Biologi Molekuler?

**Biologi molekuler** mempelajari proses biologis pada tingkat molekuler — khususnya bagaimana informasi genetik disimpan dalam DNA, diekspresikan menjadi RNA, dan diterjemahkan menjadi protein.

---

## Dogma Sentral Biologi Molekuler

```
                Replikasi
        DNA ────────────► DNA
         │
  Transkripsi
         │
         ▼
        RNA ─────────────► Protein
              Translasi
```

> **"DNA makes RNA makes Protein"** — Francis Crick, 1958

---

## DNA (Deoxyribonucleic Acid)

### Struktur DNA

DNA adalah polimer dari **nukleotida**. Setiap nukleotida terdiri dari:

```
Nukleotida = Fosfat + Gula Deoksiribosa + Basa Nitrogen
```

**4 Basa Nitrogen DNA:**

| Basa | Tipe | Pasangan |
|------|------|----------|
| Adenin (A) | Purin | T (2 ikatan H) |
| Timin (T) | Pirimidin | A (2 ikatan H) |
| Guanin (G) | Purin | C (3 ikatan H) |
| Sitosin (C) | Pirimidin | G (3 ikatan H) |

**Aturan Chargaff:** `[A] = [T]` dan `[G] = [C]`

### Struktur Heliks Ganda

```
5' ─ A─T─G─C─A─T─G─C ─ 3'   (untai sense)
     | | | | | | | |
3' ─ T─A─C─G─T─A─C─G ─ 5'   (untai antisense)

- Antiparalel: satu untai 5'→3', pasangannya 3'→5'
- Diameter: ~2 nm
- 1 putaran = 10 pasangan basa = 3.4 nm
```

### Replikasi DNA

Proses penggandaan DNA sebelum pembelahan sel.

**Model:** Semi-konservatif (setiap untai baru menggunakan 1 untai lama sebagai template)

```
Enzim-enzim kunci:
┌─────────────────┬────────────────────────────────┐
│ Helikase        │ Membuka heliks ganda (unzipping)│
│ Primase         │ Membuat primer RNA              │
│ DNA Polimerase  │ Menyintesis untai DNA baru      │
│ Ligase          │ Menyambung fragmen Okazaki      │
│ Topoisomerase   │ Mencegah supercoiling           │
└─────────────────┴────────────────────────────────┘
```

---

## RNA (Ribonucleic Acid)

### Perbedaan DNA vs RNA

| Fitur | DNA | RNA |
|-------|-----|-----|
| Gula | Deoksiribosa | Ribosa |
| Basa | A, T, G, C | A, **U**, G, C |
| Untai | Dobel | Tunggal |
| Lokasi | Nukleus | Nukleus & Sitoplasma |
| Fungsi | Menyimpan info genetik | Ekspres gen |

### Jenis-jenis RNA

| Jenis | Singkatan | Fungsi |
|-------|-----------|--------|
| mRNA | messenger RNA | Membawa instruksi dari DNA ke ribosom |
| tRNA | transfer RNA | Membawa asam amino ke ribosom |
| rRNA | ribosomal RNA | Komponen struktural ribosom |
| miRNA | micro RNA | Regulasi ekspresi gen |
| siRNA | small interfering RNA | RNA interference (silencing) |
| lncRNA | long non-coding RNA | Regulasi genomik |

---

## Transkripsi

Proses pembuatan mRNA dari template DNA.

### Tahapan Transkripsi

```
1. INISIASI
   RNA Polimerase mengikat promoter (sekuens TATA box)
   Heliks DNA terbuka

2. ELONGASI  
   RNA Polimerase bergerak sepanjang template (3'→5')
   mRNA disintesis (5'→3')
   Basa RNA: A↔U, T↔A, G↔C

3. TERMINASI
   RNA Polimerase mencapai sekuens terminator
   mRNA dilepaskan
```

### Pemrosesan mRNA (pada eukariot)

```
Pre-mRNA
  │
  ├── 5' Capping (tambah 7-metilguanosin)
  ├── 3' Polyadenylation (tambah ekor poli-A)
  └── RNA Splicing (buang intron, sambung ekson)
  │
  ▼
Mature mRNA → diekspor ke sitoplasma
```

> **Intron:** sekuens non-coding yang dibuang
> **Ekson:** sekuens coding yang dipertahankan

---

## Translasi

Proses pembuatan protein dari mRNA.

### Kode Genetik

mRNA dibaca dalam **kodon** (3 basa per kodon) → 1 asam amino

```
Tabel Kodon (sebagian):
UUU = Phe (F)    AUG = Met (M) ← Kodon Start
UUC = Phe (F)    UAA = Stop
UUA = Leu (L)    UAG = Stop
...              UGA = Stop
```

**64 kodon** → 20 asam amino (degenerasi kode genetik)

### Tahapan Translasi

```
1. INISIASI
   Ribosom kecil mengikat mRNA di kodon AUG (start)
   tRNA-Met pertama masuk ke situs P ribosom

2. ELONGASI
   tRNA baru masuk ke situs A (sesuai kodon)
   Ikatan peptida terbentuk
   Ribosom bergerak (translokasi) 3 basa ke kanan

3. TERMINASI
   Ribosom mencapai kodon stop (UAA, UAG, UGA)
   Release factor membebaskan polipeptida
```

---

## Regulasi Ekspresi Gen

### Pada Prokariot: Model Operon

```
Operon Lac (E. coli):
[Promoter][Operator][lacZ][lacY][lacA]
    ↑           ↑
RNA Pol    Repressor berikatan di sini
           (blokirtranskripsi saat ada laktosa)
```

### Pada Eukariot

| Level Regulasi | Mekanisme |
|---------------|-----------|
| Kromatin | Modifikasi histon, metilasi DNA |
| Transkripsi | Faktor transkripsi, enhancer, silencer |
| Pasca-transkripsi | Splicing alternatif, stabilitas mRNA |
| Translasi | miRNA, regulasi inisiasi |
| Pasca-translasi | Modifikasi protein, degradasi |

---

## Mutasi DNA

Perubahan pada sekuens DNA.

| Tipe Mutasi | Deskripsi | Contoh |
|-------------|-----------|--------|
| Substitusi | 1 basa diganti | A→G |
| Insersi | Basa ditambahkan | +T |
| Delesi | Basa dihapus | -C |
| Inversi | Segmen terbalik | ATCG → GCTA |
| Translokasi | Segmen pindah kromosom | |
| Frameshift | Insersi/delesi menggeser frame baca | |

**Akibat mutasi:**
- **Silent:** tidak mengubah asam amino
- **Missense:** mengubah 1 asam amino
- **Nonsense:** menghasilkan kodon stop prematur

---

## Relevansi dengan Bioinformatika

```
Biologi Molekuler → Bioinformatika

DNA sekuens    → Sequence alignment, SNP calling
mRNA sekuens   → RNA-seq analysis, differential expression
Protein        → Structure prediction, functional annotation
Regulasi gen   → ChIP-seq, ATAC-seq analysis
Mutasi         → Variant calling, cancer genomics
```

---

## Pertanyaan Latihan

1. Tuliskan sekuens mRNA dari template DNA berikut: `3'-TACGGGCTA-5'`
2. Apa perbedaan intron dan ekson?
3. Kodon apa yang menjadi sinyal "start" dan "stop" dalam translasi?
4. Mengapa kode genetik disebut "degenerate"?
5. Jelaskan mengapa mutasi frameshift biasanya lebih berbahaya dari substitusi!

---

_[← Kembali: Struktur Sel](../02-Cell-Structure/README.md) | [Lanjut: Genetika →](../04-Genetics/README.md)_
