Tugas: Lakukan refactoring nama komponen pada berkas logika formal dari nama privat ke simbol universal sesuai Kamus Pemetaan.

Langkah-langkah:
1. Perbarui kode di dalam file `.smt2` (dari protocol_09.smt2 menjadi bounded_loop.smt2), ganti semua token: P09 -> q_self, SCAN -> q_scan, SELFCHECK -> q_check, HALT -> q_halt, M -> M_inf, N -> N_steps.
2. Jalankan ulang Z3 Solver untuk mengeksekusi `bounded_loop.smt2` guna menghasilkan `bounded_loop.log` yang baru dengan status [UNSAT].
3. Sesuaikan seluruh variabel pengecekan di dalam file python penguji gerbang (menjadi bounded_loop_gate.py) agar membaca nama komponen yang baru dan pastikan 8 kondisi tetap lulus (PASS).
4. Setelah gerbang internal lulus dan menyatakan status [GENUINE], jalankan perintah `python checksum_check.py --update` untuk memperbarui manifes `CHECKSUM.sha256` di root direktori.
5. berikan rekomendasi dan alternatif tambahan refactoring nama komponen pada file atau kode yang perlu di formal dari nama privat ke simbol universal sesuai Kamus Pemetaan.