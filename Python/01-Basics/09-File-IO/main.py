"""main.py: demonstrasi File I/O tanpa mengakses sistem berkas."""

import csv
from io import BytesIO, StringIO, TextIOWrapper


def demo_teks():
    """Peragakan objek berkas teks menggunakan penyangga di memori."""
    print("=== 1. Konsep dan operasi teks ===")
    print("Berkas menyimpan data; path menunjukkan lokasinya.")
    print("Objek berkas menyediakan read(), write(), seek(), dan lainnya.")
    print("Demo ini memakai StringIO, bukan berkas di penyimpanan.")
    print("Tidak ada open() atau akses sistem berkas yang dijalankan.\n")

    # StringIO mendukung protokol objek berkas, tetapi tidak memiliki path.
    with StringIO() as berkas:
        jumlah = berkas.write("Protein: MKTAYIAK\n")
        berkas.write("Keterangan: contoh pendek\n")
        print(f"write() pertama menulis {jumlah} karakter.")
        print(f"Posisi setelah menulis: {berkas.tell()}")
        print(f"read() pada akhir data: {berkas.read()!r}")

        # Pembacaan dimulai dari posisi sekarang; putar ulang secara eksplisit.
        berkas.seek(0)
        print(f"readline(): {berkas.readline().rstrip()}")
        print(f"read() sisanya: {berkas.read().rstrip()}")

        berkas.seek(0)
        print("Iterasi per baris:")
        for nomor, baris in enumerate(berkas, start=1):
            print(f"  {nomor}. {baris.rstrip()}")

    print(f"Setelah with, objek tertutup: {berkas.closed}")
    try:
        berkas.read()
    except ValueError:
        print("Penanganan kesalahan: objek yang sudah ditutup tidak bisa dibaca.")


def demo_encoding():
    """Peragakan konversi teks ke byte UTF-8 dan kembali ke teks."""
    print("\n=== 2. Encoding UTF-8 ===")
    teks = "Anotasi: protein β\n"

    # TextIOWrapper menangani encoding di atas penyangga byte di memori.
    with BytesIO() as penyangga:
        with TextIOWrapper(penyangga, encoding="utf-8", newline="") as berkas:
            berkas.write(teks)
            berkas.flush()  # Teruskan buffer teks ke penyangga byte.
            print(f"Teks awal: {teks.rstrip()}")
            print(f"Representasi UTF-8: {penyangga.getvalue()!r}")
            berkas.seek(0)
            print(f"Hasil pembacaan: {berkas.read().rstrip()}")


def demo_tabel():
    """Tulis dan baca CSV/TSV dengan modul csv, bukan split manual."""
    print("\n=== 3. CSV dan TSV ===")
    data = [
        {"id": "dna_1", "sekuens": "ATGCGC", "catatan": "pendek, kaya GC"},
        {"id": "dna_2", "sekuens": "ATATGG", "catatan": "contoh kedua"},
    ]
    kolom = ["id", "sekuens", "catatan"]

    for nama, pemisah in (("CSV", ","), ("TSV", "\t")):
        # newline="" membiarkan modul csv mengelola akhir baris.
        with StringIO(newline="") as berkas:
            penulis = csv.DictWriter(
                berkas,
                fieldnames=kolom,
                delimiter=pemisah,
                lineterminator="\n",
            )
            penulis.writeheader()
            penulis.writerows(data)
            print(f"\nIsi {nama} (repr agar tab terlihat):")
            print(repr(berkas.getvalue()))

            berkas.seek(0)
            for baris in csv.DictReader(berkas, delimiter=pemisah):
                sekuens = baris["sekuens"]
                gc = sum(basa in "GC" for basa in sekuens)
                print(
                    f"  {baris['id']}: panjang={len(sekuens)}, "
                    f"GC={gc / len(sekuens):.1%}, "
                    f"catatan={baris['catatan']}"
                )

    print("Modul csv mempertahankan koma di dalam kolom yang diberi kutip.")


def baca_fasta_dna(berkas):
    """Baca FASTA DNA sederhana; hanya alfabet A, C, G, T, N diterima."""
    identitas = None
    bagian = []

    for nomor, baris in enumerate(berkas, start=1):
        baris = baris.strip()
        if not baris:
            continue

        if baris.startswith(">"):
            if identitas is not None:
                if not bagian:
                    raise ValueError(f"Sekuens kosong untuk {identitas!r}.")
                yield identitas, "".join(bagian)

            identitas = baris[1:].strip()
            if not identitas:
                raise ValueError(f"Header kosong pada baris {nomor}.")
            bagian = []
        else:
            if identitas is None:
                raise ValueError(f"Baris {nomor}: sekuens mendahului header.")
            sekuens = baris.upper()
            if set(sekuens) - set("ACGTN"):
                raise ValueError(f"Baris {nomor}: simbol DNA tidak didukung.")
            bagian.append(sekuens)

    if identitas is not None:
        if not bagian:
            raise ValueError(f"Sekuens kosong untuk {identitas!r}.")
        yield identitas, "".join(bagian)


def demo_fasta():
    """Peragakan sekuens multibaris dan penanganan data tidak valid."""
    print("\n=== 4. FASTA DNA ===")
    contoh = ">dna_1 contoh multibaris\nATGC\nGC\n>dna_2\nATATGG\n"
    with StringIO(contoh) as berkas:
        for identitas, sekuens in baca_fasta_dna(berkas):
            print(f"{identitas}: {sekuens}, panjang={len(sekuens)}")

    with StringIO("ATGC\n") as berkas:
        try:
            list(baca_fasta_dna(berkas))
        except ValueError as kesalahan:
            print(f"Data tidak valid ditangani: {kesalahan}")


def main():
    demo_teks()
    demo_encoding()
    demo_tabel()
    demo_fasta()

    print("\n=== 5. Panduan saat memakai berkas sungguhan ===")
    print("Pola: with open(path, mode, encoding='utf-8') as berkas:")
    print("Mode r: baca; w: tulis dan kosongkan isi lama; a: tambah di akhir.")
    print("Mode x: buat baru dan gagal jika berkas sudah ada.")
    print("Path relatif mengacu pada direktori kerja, bukan selalu lokasi skrip.")
    print("Gunakan newline='' saat membuka berkas CSV untuk modul csv.")
    print("Pilih iterasi baris untuk data besar; read() membaca seluruh sisa isi.")
    print("Tangani FileNotFoundError, PermissionError, dan UnicodeDecodeError.")
    print("Validasi struktur data dan hindari menimpa data sumber.")
    print("Seluruh demo di atas hanya memakai memori; tidak ada berkas dibuat.")


if __name__ == "__main__":
    main()
