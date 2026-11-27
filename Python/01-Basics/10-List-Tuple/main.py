"""Contoh mandiri List & Tuple dalam Python; seluruh data berada di memori."""


def judul(teks: str) -> None:
    """Cetak pemisah agar hasil demonstrasi mudah dibaca."""
    print(f"\n{'=' * 64}\n{teks}\n{'=' * 64}")


def demo_pembuatan() -> None:
    """Perkenalkan literal, konversi, urutan, dan tuple satu elemen."""
    judul("1. Membuat list dan tuple")

    panjang_sekuens = [120, 98, 145, 120]
    sampel = ("S01", "Escherichia coli", 120)
    satu_gen = ("rpoB",)
    bukan_tuple = ("rpoB")  # Tanpa koma, ini hanya string dalam kurung.
    pasangan = "S01", 120   # Packing: koma membentuk tuple.

    print("List panjang sekuens (bp):", panjang_sekuens)
    print("Urutan dipertahankan dan nilai 120 boleh berulang.")
    print("Tuple rekaman (ID, spesies, panjang):", sampel)
    print("List kosong:", [], "| Tuple kosong:", ())
    print('list("ACGT") menghasilkan:', list("ACGT"))
    print("Konversi list ke tuple:", tuple(panjang_sekuens))
    print("Konversi tuple ke list:", list(sampel))
    print("Tuple satu elemen:", satu_gen, "| Tipe:", type(satu_gen).__name__)
    print("Tanpa koma:", bukan_tuple, "| Tipe:", type(bukan_tuple).__name__)
    print("Packing tanpa kurung:", pasangan)


def demo_akses() -> None:
    """Tunjukkan indeks, slicing, pencarian, dan perulangan."""
    judul("2. Indeks, slicing, dan perulangan")

    gen = ["rpoB", "gyrA", "recA", "lacZ"]
    kodon = ("ATG", "GAA", "TAA")

    print("List gen:", gen)
    print("gen[0] (pertama):", gen[0])
    print("gen[-1] (terakhir):", gen[-1])
    print("gen[1:3] (indeks 1 disertakan, 3 tidak):", gen[1:3])
    print("gen[:2] (dua pertama):", gen[:2])
    print("gen[::2] (setiap dua langkah):", gen[::2])
    print("gen[::-1] (urutan terbalik):", gen[::-1])
    print("gen[:100] (batas slicing disesuaikan):", gen[:100])
    print("kodon[1:] tetap berupa tuple:", kodon[1:])
    print("Jumlah gen:", len(gen))
    print("Apakah 'recA' ada?", "recA" in gen)
    print("Indeks 'recA':", gen.index("recA"))
    print("Jumlah kemunculan 'ATG':", kodon.count("ATG"))

    print("Penelusuran dengan enumerate (nomor tampilan mulai dari 1):")
    for nomor, nama in enumerate(gen, start=1):
        print(f"  {nomor}. {nama}")

    # Tangani kesalahan yang sengaja dibuat agar program tetap berjalan.
    try:
        print(gen[100])
    except IndexError:
        print("gen[100] menimbulkan IndexError: indeks di luar rentang.")


def demo_mutabilitas() -> None:
    """Bandingkan perubahan list dengan sifat immutable pada tuple."""
    judul("3. Mutabilitas dan operasi list")

    gen = ["rpoB", "gyrA", "recA"]
    print("List awal:", gen)

    gen[1] = "lacZ"
    print("Setelah gen[1] = 'lacZ':", gen)

    gen.append("dnaK")
    print("Setelah append('dnaK'):", gen)

    gen.extend(["groEL", "rpoB"])
    print("Setelah extend(['groEL', 'rpoB']):", gen)

    gen.insert(1, "gyrA")
    print("Setelah insert(1, 'gyrA'):", gen)

    gen.remove("rpoB")  # Hanya menghapus kemunculan pertama.
    print("Setelah remove('rpoB'):", gen)

    terakhir = gen.pop()
    print(f"pop() mengambil {terakhir!r}; list tersisa: {gen}")

    print("sorted(gen) membuat list baru:", sorted(gen))
    print("List asli setelah sorted():", gen)
    gen.sort()  # Mengurutkan langsung; nilai baliknya adalah None.
    print("List asli setelah sort():", gen)

    kodon = ("ATG", "GAA", "TAA")
    try:
        kodon[0] = "GTG"
    except TypeError:
        print("Tuple menolak penggantian elemen: kodon[0] = 'GTG'.")

    # Penggabungan menghasilkan tuple baru, bukan mengubah tuple lama.
    diperluas = kodon + ("TAG",)
    print("Tuple asli:", kodon)
    print("Tuple baru hasil penggabungan:", diperluas)

    # Immutable berarti referensi elemen tuple tidak bisa diganti.
    # Objek mutable di dalam tuple tetap dapat berubah.
    rekaman = ("S01", [2.4, 3.1])
    rekaman[1].append(2.8)
    print("List di dalam tuple masih dapat diubah:", rekaman)


def demo_penyalinan() -> None:
    """Bedakan alias, salinan dangkal, dan salinan mendalam."""
    from copy import deepcopy  # Modul standard library.

    judul("4. Penyalinan: alias, shallow copy, dan deep copy")

    asli = [120, 98, 145]
    alias = asli
    salinan = asli.copy()  # Untuk list datar ini, asli[:] juga memadai.
    alias.append(80)

    print("asli setelah alias.append(80):", asli)
    print("alias is asli:", alias is asli)
    print("Salinan list sebelum perubahan:", salinan)
    print("salinan is asli:", salinan is asli)

    pengukuran = [["S01", 2.4], ["S02", 3.1]]
    dangkal = pengukuran.copy()
    mendalam = deepcopy(pengukuran)
    pengukuran[0][1] = 9.9

    print("Data bersarang setelah nilai S01 diubah:", pengukuran)
    print("Shallow copy berbagi list bagian dalam:", dangkal)
    print("Deep copy tidak ikut berubah:", mendalam)


def persen_gc(dna: str) -> float:
    """Hitung persen G/C pada DNA ACGT; tolak data kosong atau tidak valid."""
    dna = dna.upper()
    if not dna or any(basa not in "ACGT" for basa in dna):
        raise ValueError("DNA harus tidak kosong dan hanya mengandung A, C, G, T.")
    return 100 * (dna.count("G") + dna.count("C")) / len(dna)


def analisis_sampel(
    sampel: list[tuple[str, str]],
) -> list[tuple[str, int, float]]:
    """Kembalikan list rekaman tuple: (ID, panjang_bp, GC_persen)."""
    return [
        (identitas, len(dna), persen_gc(dna))
        for identitas, dna in sampel
    ]


def demo_analisis() -> None:
    """Integrasikan comprehension, fungsi, packing, dan unpacking."""
    judul("5. Analisis bioinformatika sederhana tanpa berkas")

    # List cocok untuk koleksi yang dapat ditambah atau disaring.
    # Tuple cocok untuk rekaman dengan susunan kolom yang tetap.
    sampel = [
        ("S01", "ATGCGTAC"),
        ("S02", "GGCCGG"),
        ("S03", "ATATAT"),
        ("S04", "ACGTACGTAA"),
    ]
    sampel.append(("S05", "GCGCATGC"))

    print("Data ditulis langsung di kode, tanpa pembacaan berkas:")
    for identitas, dna in sampel:  # Unpacking setiap tuple.
        print(f"  {identitas}: {dna}")

    hasil = analisis_sampel(sampel)
    print("\nHasil: ID | panjang (bp) | GC (%)")
    for identitas, panjang, gc in hasil:
        print(f"  {identitas} | {panjang:2d} | {gc:6.2f}")

    panjang_sekuens = [panjang for _, panjang, _ in hasil]
    lolos = [
        identitas
        for identitas, panjang, gc in hasil
        if panjang >= 8 and gc >= 50
    ]
    urut_gc = sorted(hasil, key=lambda rekaman: rekaman[2], reverse=True)

    print("\nList comprehension panjang sekuens:", panjang_sekuens)
    print(f"Rata-rata panjang: {sum(panjang_sekuens) / len(panjang_sekuens):.2f} bp")
    print("Sampel dengan panjang >= 8 bp dan GC >= 50%:", lolos)
    print("ID menurut GC menurun:", [rekaman[0] for rekaman in urut_gc])

    terbaik, *lainnya = urut_gc  # Extended unpacking; lainnya berupa list.
    identitas, panjang, gc = terbaik
    print(f"GC tertinggi: {identitas}, {panjang} bp, {gc:.2f}%")
    print("Jumlah rekaman lainnya setelah unpacking:", len(lainnya))


def main() -> None:
    """Jalankan seluruh demonstrasi dengan data kecil dan deterministik."""
    print("LIST & TUPLE DALAM PYTHON — contoh biologis")
    demo_pembuatan()
    demo_akses()
    demo_mutabilitas()
    demo_penyalinan()
    demo_analisis()

    judul("Ringkasan pemilihan struktur data")
    print("LIST : koleksi berurutan yang elemennya dapat ditambah atau diubah.")
    print("TUPLE: rekaman berurutan yang referensi elemennya tidak dapat diganti.")
    print("Keduanya mendukung indeks, slicing, perulangan, dan nilai berulang.")
    print("Waspadai alias dan objek mutable yang tersimpan di dalam koleksi.")


if __name__ == "__main__":
    main()
