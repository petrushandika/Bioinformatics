"""main.py: contoh fungsi dan modul untuk analisis DNA sederhana.

File ini juga merupakan modul: fungsi-fungsinya dapat diimpor dengan
`from main import hitung_gc` tanpa menjalankan demonstrasi dalam main().
Semua data contoh ditulis langsung di kode; tidak ada akses berkas/jaringan.
"""

# Mengimpor fungsi dan kelas dari modul pustaka standar Python.
from collections import Counter
from math import isclose
from statistics import mean


def validasi_dna(sekuens: str) -> str:
    """Kembalikan DNA huruf besar; tolak tipe, sekuens kosong, atau basa ilegal."""
    if not isinstance(sekuens, str):
        raise TypeError("Sekuens DNA harus berupa string.")

    # Variabel ini bersifat lokal: tidak mengubah argumen milik pemanggil.
    dna = sekuens.strip().upper()
    if not dna:
        raise ValueError("Sekuens DNA tidak boleh kosong.")

    basa_ilegal = set(dna) - set("ATGC")
    if basa_ilegal:
        raise ValueError(f"Basa tidak valid: {', '.join(sorted(basa_ilegal))}.")

    return dna


def panjang_sekuens(sekuens: str) -> int:
    """Kembalikan jumlah basa setelah validasi."""
    return len(validasi_dna(sekuens))


def hitung_gc(sekuens: str) -> float:
    """Kembalikan persentase G dan C pada DNA nonkosong."""
    dna = validasi_dna(sekuens)
    jumlah = Counter(dna)
    return (jumlah["G"] + jumlah["C"]) / len(dna) * 100


def komplemen_balik(sekuens: str) -> str:
    """Kembalikan reverse complement, ditulis dalam arah 5' ke 3'."""
    dna = validasi_dna(sekuens)
    tabel_komplemen = str.maketrans("ATGC", "TACG")
    return dna.translate(tabel_komplemen)[::-1]


def label_sampel(nama: str, organisme: str = "Escherichia coli") -> str:
    """Gunakan nilai bawaan jika argumen organisme tidak diberikan."""
    return f"{nama} ({organisme})"


def tambah_sampel(nama: str, daftar: list[str] | None = None) -> list[str]:
    """Tambahkan nama; buat daftar baru jika pemanggil tidak menyediakan daftar."""
    # Jangan memakai daftar=[] sebagai nilai bawaan karena dapat dipakai bersama.
    if daftar is None:
        daftar = []
    daftar.append(nama)
    return daftar


def tampilkan_gc(sekuens: str) -> None:
    """Cetak GC untuk pengguna, bukan mengembalikan angka untuk perhitungan."""
    print(f"  Tampilan dari print(): GC = {hitung_gc(sekuens):.2f}%")
    # Tanpa return eksplisit, fungsi mengembalikan None.


def uji_fungsi() -> int:
    """Jalankan pengujian kecil dan kembalikan jumlah pemeriksaan yang lolos."""
    pemeriksaan = [
        (validasi_dna(" atgc ") == "ATGC", "Normalisasi DNA"),
        (panjang_sekuens("ATGCGT") == 6, "Panjang sekuens"),
        (isclose(hitung_gc("ATGC"), 50.0), "GC campuran"),
        (isclose(hitung_gc("GCGC"), 100.0), "GC maksimum"),
        (isclose(hitung_gc("AATT"), 0.0), "GC minimum"),
        (komplemen_balik("ATGCC") == "GGCAT", "Komplemen balik"),
        (tambah_sampel("A") == ["A"], "Daftar bawaan pertama"),
        (tambah_sampel("B") == ["B"], "Daftar bawaan tidak dibagi"),
    ]

    for lolos, deskripsi in pemeriksaan:
        if not lolos:
            raise AssertionError(f"Pengujian gagal: {deskripsi}")

    jumlah_lolos = len(pemeriksaan)
    for masukan, jenis_error in [
        ("", ValueError),
        ("ATGN", ValueError),
        (123, TypeError),
    ]:
        try:
            validasi_dna(masukan)
        except jenis_error:
            jumlah_lolos += 1
        else:
            raise AssertionError(f"Masukan {masukan!r} seharusnya ditolak.")

    return jumlah_lolos


def main() -> None:
    """Susun demonstrasi tanpa mencampurkan analisis dengan interaksi pengguna."""
    print("=== Fungsi & Modul dalam Python: Analisis DNA ===")

    print("\n1. Parameter, argumen posisi, argumen bernama, dan nilai bawaan")
    print("  Parameter adalah nama pada def; argumen adalah nilai saat pemanggilan.")
    print(f"  Nilai bawaan: {label_sampel('Sampel_A')}")
    print(
        "  Argumen bernama:",
        label_sampel(nama="Sampel_B", organisme="Saccharomyces cerevisiae"),
    )
    print(f"  Argumen posisi: panjang_sekuens('ATGCGT') = {panjang_sekuens('ATGCGT')}")

    print("\n2. return berbeda dari print()")
    nilai_gc = hitung_gc("ATGC")
    print(f"  return memberi angka: {nilai_gc:.2f}; dapat dibagi dua = {nilai_gc / 2:.2f}")
    hasil_tampilan = tampilkan_gc("ATGC")
    print(f"  Nilai kembalian fungsi tampilan: {hasil_tampilan!r}")

    print("\n3. Ruang lingkup variabel")
    sekuens = " atgc "
    dna_bersih = validasi_dna(sekuens)
    print(f"  Variabel sekuens di main() tetap: {sekuens!r}")
    print(f"  Hasil variabel lokal dna dikembalikan sebagai: {dna_bersih!r}")

    print("\n4. Fungsi yang digunakan ulang dan modul pustaka standar")
    sampel = [
        ("Sampel_A", "ATGCGT"),
        ("Sampel_B", "GGCCAA"),
        ("Sampel_C", "AATTAT"),
    ]
    daftar_gc = []
    for nama, dna in sampel:
        gc = hitung_gc(dna)
        daftar_gc.append(gc)
        print(
            f"  {nama}: DNA={dna}, panjang={panjang_sekuens(dna)} basa, "
            f"GC={gc:.2f}%, komplemen balik={komplemen_balik(dna)}"
        )

    print(f"  Rata-rata GC antarsampel (statistics.mean): {mean(daftar_gc):.2f}%")
    print("  Counter dari collections menghitung basa di dalam hitung_gc().")
    print("  main.py adalah modul; penjaga __main__ mencegah demo berjalan saat diimpor.")

    print("\n5. Nilai bawaan yang aman untuk daftar")
    daftar_a = tambah_sampel("A")
    daftar_b = tambah_sampel("B")
    print(f"  Dua pemanggilan membuat daftar terpisah: {daftar_a} dan {daftar_b}")
    tambah_sampel("C", daftar=daftar_a)
    print(f"  Daftar eksplisit dapat ditambah: {daftar_a}")

    print("\n6. Validasi masukan dan pengujian")
    for masukan in ("ATGN", "", 123):
        try:
            hitung_gc(masukan)
        except (TypeError, ValueError) as error:
            print(f"  Masukan {masukan!r} ditolak: {error}")

    print(f"  Hasil pengujian otomatis: {uji_fungsi()} pemeriksaan lulus.")


if __name__ == "__main__":
    main()
