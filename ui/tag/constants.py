import chainlit as cl

TAG_DESC = """
Sistem tanya jawab berbasis Table-Augmented Generation (TAG) untuk menjawab pertanyaan hukum berdasarkan data tabel.
"""

TAG_STARTERS = [
    cl.Starter(
        label="Penyadapan dalam UU ITE",
        message="Apa yang dimaksud dengan 'intersepsi' atau 'penyadapan' dalam UU Nomor 11 Tahun 2008 tentang Informasi dan Transaksi Elektronik, dan apakah semua tindakan penyadapan dilarang?",
        icon="/public/idea.svg",
    ),
    cl.Starter(
        label="Judul Peraturan Pemerintah",
        message="Apa judul dari Peraturan Pemerintah (PP) Nomor 80 Tahun 2019?",
        icon="/public/idea.svg",
    ),
    cl.Starter(
        label="Isi Pasal",
        message="Apa isi Pasal 2 Peraturan Pemerintah (PP) Nomor 80 Tahun 2019?",
        icon="/public/idea.svg",
    )
]


TAG_SETTINGS = []
# Kalau kamu mau menambahkan settings seperti dropdown model, kamu bisa isi nanti.
