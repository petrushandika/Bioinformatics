"""Contoh mandiri Dictionary & Set dalam Python (Python 3.12).

Semua data bersifat ilustratif dan ditulis langsung di dalam kode.
Tidak memerlukan input pengguna, berkas, jaringan, atau pustaka tambahan.
"""


def judul(teks: str) -> None:
    """Cetak pembatas agar setiap bagian mudah dikenali."""
    print(f"\n=== {teks} ===")


def bandingkan_struktur_data() -> None:
    """Bandingkan urutan, duplikasi, pemetaan, dan keanggotaan."""
    judul("1. Memilih list, tuple, dictionary, atau set")

    daftar = ["GEN_A", "GEN_B", "GEN_A"]
    koordinat = ("kromosom_1", 100, 250)
    panjang = {"GEN_A": 900, "GEN_B": 750}
    gen_unik = set(daftar)

    print("List: urutan dapat diubah dan duplikasi dipertahankan:", daftar)
    print("Tuple: urutan tetap; elemen tidak dapat diganti:", koordinat)
    print("Dictionary: memetakan kunci ke nilai:", panjang)
    print("Set: menyimpan elemen unik:", sorted(gen_unik))
    print("Panjang GEN_A melalui kunci:", panjang["GEN_A"])
    print("Apakah GEN_B termasuk gen unik?", "GEN_B" in gen_unik)
    print("sorted(set) menghasilkan list terurut untuk tampilan konsisten.")
    print("Set sendiri tidak memiliki jaminan urutan atau akses indeks.")


def kelola_dictionary() -> None:
    """Demonstrasikan pembuatan, akses, perubahan, dan penghapusan."""
    judul("2. Operasi dasar dictionary")

    gen = {
        "simbol": "GEN_A",
        "panjang_nt": 900,
        "organisme": "organisme_contoh",
    }
    print("Data awal:", gen)
    print("Akses kunci wajib, gen['simbol']:", gen["simbol"])
    print("Kunci opsional melalui get():", gen.get("fungsi"))
    print("get() dengan nilai pengganti:", gen.get("fungsi", "Belum diketahui"))

    gen["fungsi"] = "Belum dianotasi"  # Tambahkan kunci baru.
    gen["panjang_nt"] = 930  # Ganti nilai pada kunci yang sudah ada.
    gen.update({"organisme": "sampel_A", "status": "ditinjau"})
    print("Setelah penambahan dan pembaruan:", gen)

    del gen["status"]
    fungsi = gen.pop("fungsi", "Tidak tersedia")
    print("Nilai yang diambil sekaligus dihapus dengan pop():", fungsi)
    print("Setelah penghapusan:", gen)
    print("pop() pada kunci yang tidak ada:", gen.pop("fungsi", "Tidak tersedia"))

    print("Iterasi pasangan menggunakan items():")
    for kunci, nilai in gen.items():
        print(f"  {kunci} -> {nilai}")

    # Dictionary mempertahankan urutan penyisipan, bukan urutan alfabetis.
    print("Urutan kunci sesuai penyisipan:", list(gen))
    print("'simbol' in gen memeriksa kunci:", "simbol" in gen)
    print("'GEN_A' in gen.values() memeriksa nilai:", "GEN_A" in gen.values())

    # Penugasan kedua mengganti nilai; tidak menciptakan kunci duplikat.
    pengukuran = {"GEN_A": 10}
    pengukuran["GEN_A"] = 25
    print("Kunci berulang mengganti nilai sebelumnya:", pengukuran)


def hitung_nukleotida(sekuens: str) -> dict[str, int]:
    """Hitung A, C, G, T, dan N; tolak simbol lain secara eksplisit."""
    sekuens = sekuens.upper()
    simbol_asing = set(sekuens) - set("ACGTN")
    if simbol_asing:
        raise ValueError(f"Simbol DNA tidak didukung: {sorted(simbol_asing)}")

    # Semua basa tetap tersedia sebagai kunci, termasuk yang berjumlah nol.
    hitungan = {basa: 0 for basa in "ACGTN"}
    for basa in sekuens:
        hitungan[basa] += 1
    return hitungan


def analisis_dna() -> None:
    """Terapkan dictionary untuk penghitungan dan pemetaan panjang."""
    judul("3. Menghitung nukleotida")

    sekuens = {
        "seq_A": "ACGTACGTNN",
        "seq_B": "GGCCAT",
        "seq_C": "",
    }
    panjang = {identitas: len(dna) for identitas, dna in sekuens.items()}
    print("Pemetaan identitas ke panjang sekuens:", panjang)

    for identitas, dna in sekuens.items():
        hitungan = hitung_nukleotida(dna)
        # N adalah basa tak diketahui, sehingga dikeluarkan dari penyebut GC.
        jumlah_basa_dikenal = sum(hitungan[basa] for basa in "ACGT")
        if jumlah_basa_dikenal:
            gc = 100 * (hitungan["G"] + hitungan["C"]) / jumlah_basa_dikenal
            keterangan_gc = f"{gc:.1f}%"
        else:
            keterangan_gc = "tidak terdefinisi (tidak ada basa A/C/G/T)"

        print(f"{identitas}: DNA={dna!r}, hitungan={hitungan}")
        print(f"  GC di antara basa A/C/G/T: {keterangan_gc}")

    try:
        hitung_nukleotida("ACGTX")
    except ValueError as kesalahan:
        print("Validasi data menangkap kesalahan:", kesalahan)


def kelompokkan_taksonomi() -> None:
    """Gunakan dictionary dengan nilai berupa set untuk menghapus duplikasi."""
    judul("4. Mengelompokkan spesies berdasarkan genus")

    pengamatan = [
        ("Escherichia", "coli"),
        ("Bacillus", "subtilis"),
        ("Escherichia", "fergusonii"),
        ("Escherichia", "coli"),  # Pengamatan berulang, bukan spesies baru.
        ("Bacillus", "cereus"),
    ]

    kelompok: dict[str, set[str]] = {}
    for genus, spesies in pengamatan:
        # setdefault() membuat set kosong hanya jika kunci belum tersedia.
        kelompok.setdefault(genus, set()).add(spesies)

    print("Jumlah catatan pengamatan:", len(pengamatan))
    for genus, spesies_unik in sorted(kelompok.items()):
        nama_lengkap = [f"{genus} {spesies}" for spesies in sorted(spesies_unik)]
        print(f"  {genus}: {len(spesies_unik)} spesies unik -> {nama_lengkap}")


def kelola_dan_bandingkan_set() -> None:
    """Demonstrasikan mutasi set serta operasi himpunan pada daftar gen."""
    judul("5. Operasi dasar set dan perbandingan daftar gen")

    teramati: set[str] = set()  # {} membuat dictionary kosong, bukan set.
    teramati.add("GEN_A")
    teramati.add("GEN_A")  # Penambahan ulang tidak mengubah jumlah elemen.
    teramati.update(["GEN_B", "GEN_C"])
    print("Set setelah add() dan update():", sorted(teramati))

    teramati.remove("GEN_C")  # remove() mewajibkan elemen tersedia.
    teramati.discard("GEN_X")  # discard() aman jika elemen tidak tersedia.
    print("Set setelah remove() dan discard():", sorted(teramati))

    sampel_a = {"GEN_A", "GEN_B", "GEN_C"}
    sampel_b = {"GEN_B", "GEN_C", "GEN_D"}
    print("Gen sampel A:", sorted(sampel_a))
    print("Gen sampel B:", sorted(sampel_b))
    print("Gabungan A | B:", sorted(sampel_a | sampel_b))
    print("Irisan A & B (gen bersama):", sorted(sampel_a & sampel_b))
    print("Selisih A - B (khusus A):", sorted(sampel_a - sampel_b))
    print("Selisih B - A (khusus B):", sorted(sampel_b - sampel_a))
    print("Beda simetris A ^ B (hanya salah satu):", sorted(sampel_a ^ sampel_b))
    print("Apakah gen bersama merupakan subset A?", (sampel_a & sampel_b) <= sampel_a)
    print("Apakah A dan B tidak beririsan?", sampel_a.isdisjoint(sampel_b))


def contoh_kesalahan_umum() -> None:
    """Tangkap kesalahan yang disengaja agar program tetap selesai."""
    judul("6. Kesalahan umum: kunci, elemen, dan hashability")

    gen = {"simbol": "GEN_A"}
    try:
        print(gen[0])
    except KeyError:
        print("KeyError: gen[0] mencari kunci 0, bukan pasangan pertama.")

    try:
        {"GEN_A"}.remove("GEN_X")
    except KeyError:
        print("KeyError: remove() gagal untuk elemen yang tidak tersedia.")

    try:
        set().add(["GEN_A", "GEN_B"])
    except TypeError:
        print("TypeError: list tidak hashable, sehingga tidak bisa menjadi elemen set.")

    try:
        data = {}
        data[["kromosom_1", 100]] = "GEN_A"
    except TypeError:
        print("TypeError: list juga tidak bisa menjadi kunci dictionary.")

    # Tuple boleh menjadi kunci jika seluruh elemennya juga hashable.
    anotasi = {("kromosom_1", 100): "GEN_A"}
    print("Tuple berisi string dan integer dapat menjadi kunci:", anotasi)
    print("Nilai dictionary boleh berupa list:", {"gen": ["GEN_A", "GEN_B"]})
    print("Tidak semua tuple hashable: tuple yang memuat list tetap tidak hashable.")


def main() -> None:
    """Jalankan seluruh contoh pembelajaran."""
    print("DICTIONARY & SET DALAM PYTHON")
    bandingkan_struktur_data()
    kelola_dictionary()
    analisis_dna()
    kelompokkan_taksonomi()
    kelola_dan_bandingkan_set()
    contoh_kesalahan_umum()
    print("\nRingkasan: dict untuk pemetaan; set untuk keunikan dan operasi himpunan.")


if __name__ == "__main__":
    main()
